(async function(){
 const targets=document.querySelectorAll('[data-auto-publications]');if(!targets.length)return;
 try{const response=await fetch('/data/publications.json',{cache:'no-cache'});if(!response.ok)throw Error('feed unavailable');const entries=await response.json();
 for(const target of targets){const max=Number(target.dataset.limit||15);const type=target.dataset.type||'all';const filtered=entries.filter(x=>type==='all'||x.type===type||type==='commentary'&&x.type==='article').slice(0,max);const ul=document.createElement('ul');ul.className='auto-publication-list';
 for(const item of filtered){const li=document.createElement('li');const a=document.createElement('a');a.href=item.url;a.textContent=item.title;a.target='_blank';a.rel='noopener noreferrer';li.append(a);const small=document.createElement('small');small.textContent=' — '+item.publisher+(item.date?' · '+item.date:'');li.append(small);
 for(const rep of item.republished||[]){const label=document.createElement('small');label.textContent=' · Republished: ';const link=document.createElement('a');link.href=rep.url;link.textContent=rep.publisher;link.target='_blank';link.rel='noopener noreferrer';label.append(link);li.append(label)}ul.append(li)}target.replaceChildren(ul)}
 }catch(err){console.warn('Publication feed not available',err)}
})();
