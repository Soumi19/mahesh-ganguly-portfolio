(async function () {
  const targets = document.querySelectorAll('[data-auto-publications]');
  if (!targets.length) return;
  try {
    const response = await fetch('/data/publications.json', {cache: 'no-cache'});
    if (!response.ok) throw new Error('Publication feed unavailable');
    const entries = await response.json();
    if (!Array.isArray(entries)) return;
    const normalize = s => String(s || '').toLowerCase().replace(/[’‘]/g, "'").replace(/[^a-z0-9]+/g, ' ').trim();
    const normalizedURL = s => { try { const u = new URL(s, location.origin); return (u.hostname.replace(/^www\./, '') + u.pathname).replace(/\/$/, '').toLowerCase(); } catch { return ''; } };
    for (const target of targets) {
      const max = Number(target.dataset.limit || 20);
      const type = target.dataset.type || 'all';
      const home = target.dataset.style === 'home';
      const existing = [...target.querySelectorAll('li')];
      const existingTitles = new Set(existing.map(li => normalize((li.querySelector('a') || li).textContent)));
      const existingURLs = new Set(existing.flatMap(li => [...li.querySelectorAll('a[href]')].map(a => normalizedURL(a.href))));
      const filtered = entries.filter(item => item && item.verified === true && (type === 'all' || item.type === type || (type === 'commentary' && ['article', 'commentary'].includes(item.type))))
        .sort((a,b) => String(b.date || '').localeCompare(String(a.date || ''))).slice(0,max);
      const added = new Set();
      for (const item of filtered) {
        const title = normalize(item.title);
        const url = normalizedURL(item.url);
        if (!item.title || !item.url || existingTitles.has(title) || (url && existingURLs.has(url)) || added.has(title)) continue;
        added.add(title);
        const li = document.createElement('li');
        if (home) li.className = 'pub-item';
        const link = document.createElement('a');
        link.href = item.url;
        link.textContent = item.title;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        if (home) link.className = 'pub-title';
        li.appendChild(link);
        if (home) {
          const outlet = document.createElement('span');
          outlet.className = 'pub-outlet';
          outlet.textContent = item.publisher || 'Publication';
          li.appendChild(outlet);
          const brief = document.createElement('p');
          brief.className = 'pub-brief';
          brief.textContent = item.description || (item.date ? 'Published ' + item.date + '.' : 'Read the full publication at the original source.');
          li.appendChild(brief);
        } else {
          li.appendChild(document.createTextNode(' — ' + (item.publisher || 'Publication') + (item.date ? ' · ' + item.date : '')));
        }
        if (Array.isArray(item.republished)) for (const rep of item.republished) {
          if (!rep.url) continue;
          const extra = document.createElement(home ? 'p' : 'span');
          if (home) extra.className = 'pub-brief';
          extra.appendChild(document.createTextNode(' Republished: '));
          const a = document.createElement('a');
          a.href = rep.url; a.textContent = rep.publisher || 'Source';
          a.target = '_blank'; a.rel = 'noopener noreferrer';
          extra.appendChild(a); li.appendChild(extra);
        }
        target.insertBefore(li, target.firstElementChild);
      }
    }
  } catch (error) { console.warn('Publication feed not available:', error); }
})();
