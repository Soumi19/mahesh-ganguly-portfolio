"""Discover articles and scholarly works; publish only high-confidence matches.
Uncertain results are written to a review queue, never presented as verified.
"""
import datetime, difflib, html, json, os, pathlib, re, urllib.parse
import requests
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; PUB=DATA/'publications.json'; QUEUE=DATA/'publication-review.json'
SESSION=requests.Session(); SESSION.headers.update({'User-Agent':'MaheshGangulyPortfolio/2.0 (public academic bibliography; contact: maheshganguly126@gmail.com)'})
NAME='mahesh ganguly'
def norm(s):return re.sub(r'[^a-z0-9]+',' ',html.unescape(str(s)).lower()).strip()
def canonical(url):
 p=urllib.parse.urlsplit(url);return urllib.parse.urlunsplit((p.scheme,p.netloc.lower(),p.path.rstrip('/'),'', ''))
def get(url):
 r=SESSION.get(url,timeout=18);r.raise_for_status();return r

def authors_match(authors):
 return any(norm(a)=='mahesh ganguly' or norm(a)=='ganguly mahesh' for a in authors)
def add(candidate,entries,queue,verified=False):
 title=candidate.get('title','').strip();url=candidate.get('url','').strip()
 if not title or not url or not url.startswith('https://'):return
 key=norm(title);found=None
 for entry in entries:
  if canonical(entry['url'])==canonical(url) or (key and difflib.SequenceMatcher(None,key,norm(entry['title'])).ratio()>=0.94):found=entry;break
 if found:
  if canonical(found['url'])!=canonical(url):
   repubs=found.setdefault('republished',[])
   if not any(canonical(x['url'])==canonical(url) for x in repubs):repubs.append({'publisher':candidate.get('publisher',''), 'url':url})
  return
 if any(canonical(x['url'])==canonical(url) for x in queue):return
 if verified: candidate['verified']=True;entries.append(candidate)
 else:candidate['verified']=False;queue.append(candidate)

def publisher_page(url):
 try:
  r=get(url)
  if len(r.content)>1500000:return None
  soup=BeautifulSoup(r.text,'html.parser')
  def meta(*keys):
   for k in keys:
    tag=soup.find('meta',attrs={'name':k}) or soup.find('meta',attrs={'property':k})
    if tag and tag.get('content'):return tag['content']
   return ''
  title=meta('og:title','twitter:title') or (soup.title.get_text(' ',strip=True) if soup.title else '')
  authors=[]
  for key in ['author','article:author','parsely-author','dc.creator','citation_author']:
   for tag in soup.find_all('meta',attrs={'name':key})+soup.find_all('meta',attrs={'property':key}):authors.append(tag.get('content',''))
  for script in soup.find_all('script',type='application/ld+json'):
   try:
    obj=json.loads(script.string or script.get_text());stack=[obj]
    while stack:
     node=stack.pop()
     if isinstance(node,list):stack.extend(node)
     elif isinstance(node,dict):
      if 'author' in node:
       aa=node['author'] if isinstance(node['author'],list) else [node['author']]
       authors.extend(a.get('name','') if isinstance(a,dict) else str(a) for a in aa)
      stack.extend(v for k,v in node.items() if k in ('@graph','mainEntity','itemListElement'))
   except (ValueError,TypeError):pass
  return {'title':title,'url':r.url,'authors':authors,'date':(meta('article:published_time','datePublished','citation_publication_date') or '')[:10], 'publisher':urllib.parse.urlsplit(r.url).netloc}
 except Exception as e:print('publisher unavailable:',url,str(e)[:100]);return None

def news(entries,queue):
 # Google News RSS is discovery only; never publish on headline matching alone.
 queries=['"Mahesh Ganguly"','"Dr Mahesh Ganguly"']
 for q in queries:
  try:
   feed=get('https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q+' when:30d','hl':'en-IN','gl':'IN','ceid':'IN:en'})).text
   soup=BeautifulSoup(feed,'xml')
   for item in soup.find_all('item')[:80]:
    link=item.link.get_text(strip=True) if item.link else ''
    if not link:continue
    try:
     page=publisher_page(link)
     if not page or 'news.google.com' in urllib.parse.urlsplit(page['url']).netloc:continue
     candidate={'title':re.sub(r'\s+[-|]\s+[^-|]+$','',page['title']),'url':page['url'],'publisher':page['publisher'],'date':page['date'],'type':'article','source':'publisher metadata'}
     add(candidate,entries,queue,authors_match(page['authors']))
    except Exception as e:print('news item skipped',str(e)[:90])
  except Exception as e:print('news feed unavailable:',str(e)[:100])

def scholarly(entries,queue):
 # OpenAlex author ID / ORCID, when configured, are reliable identity constraints.
 author_id=os.environ.get('MAHESH_OPENALEX_AUTHOR_ID','').strip()
 orcid=os.environ.get('MAHESH_ORCID','').strip()
 if author_id or orcid:
  filter_value='authorships.author.id:'+author_id if author_id else 'author.orcid:https://orcid.org/'+orcid
  try:
   payload=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':filter_value,'per-page':100,'sort':'publication_date:desc'})).json()
   for w in payload.get('results',[]):
    url=w.get('doi') or (w.get('primary_location') or {}).get('landing_page_url') or w.get('id')
    if not url:continue
    add({'title':w.get('display_name',''),'url':url,'publisher':((w.get('primary_location') or {}).get('source') or {}).get('display_name') or 'OpenAlex','date':w.get('publication_date',''),'type':w.get('type','research'),'source':'verified OpenAlex author profile'},entries,queue,True)
  except Exception as e:print('OpenAlex unavailable:',str(e)[:100])
 # Broad scholarly name search is only a review queue, never auto-verified.
 try:
  payload=get('https://api.crossref.org/works?'+urllib.parse.urlencode({'query.author':'Mahesh Ganguly','rows':30,'select':'DOI,title,author,published,container-title,type'})).json()
  for w in payload.get('message',{}).get('items',[]):
   authors=[a.get('given','')+' '+a.get('family','') for a in w.get('author',[])]
   if not authors_match(authors):continue
   date_parts=(w.get('published') or {}).get('date-parts',[[None]])[0]
   date='-'.join(str(x).zfill(2) if i else str(x) for i,x in enumerate(date_parts) if x)
   add({'title':(w.get('title') or [''])[0],'url':'https://doi.org/'+w['DOI'],'publisher':(w.get('container-title') or ['Crossref'])[0],'date':date,'type':w.get('type','research'),'source':'Crossref author-name match; identity unconfirmed'},entries,queue,False)
 except Exception as e:print('Crossref unavailable:',str(e)[:100])
 # Google Books results: author-name match only, identity must be reviewed.
 try:
  payload=get('https://www.googleapis.com/books/v1/volumes?'+urllib.parse.urlencode({'q':'inauthor:"Mahesh Ganguly"','maxResults':40})).json()
  for v in payload.get('items',[]):
   info=v.get('volumeInfo',{});
   if not authors_match(info.get('authors',[])):continue
   url=info.get('infoLink') or v.get('selfLink','')
   add({'title':info.get('title',''),'url':url,'publisher':info.get('publisher','Google Books'),'date':info.get('publishedDate',''),'type':'book','source':'Google Books author-name match; identity unconfirmed'},entries,queue,False)
 except Exception as e:print('Google Books unavailable:',str(e)[:100])

def main():
 entries=json.loads(PUB.read_text());queue=json.loads(QUEUE.read_text()) if QUEUE.exists() else []
 # BRICS republication of Hindustan Times article, confirmed from user-supplied page.
 brics='https://www.brics-info.org/3954688a93f0008a70bacf1e7efc9eaf/'
 entries=[x for x in entries if canonical(x['url'])!=canonical(brics)]
 ht='https://www.hindustantimes.com/ht-insight/international-affairs/brics-why-india-s-bet-on-practical-ties-matters-101790161275037.html'
 add({'title':'BRICS: Why India’s Bet on Practical Ties Matters','url':ht,'publisher':'Hindustan Times','date':'2026-09-23','type':'article','source':'original publication'},entries,queue,True)
 for x in entries:
  if canonical(x['url'])==canonical(ht):
   x.setdefault('republished',[])
   if not any(canonical(y['url'])==canonical(brics) for y in x['republished']):x['republished'].append({'publisher':'BRICS Information Sharing & Exchanging Platform','url':brics})
 scholarly(entries,queue);news(entries,queue)
 entries.sort(key=lambda x:x.get('date',''),reverse=True);queue.sort(key=lambda x:x.get('date',''),reverse=True)
 PUB.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n');QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
 print('Verified entries:',len(entries),'Needs review:',len(queue))
if __name__=='__main__':main()
