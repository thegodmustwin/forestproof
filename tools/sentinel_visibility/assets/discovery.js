/* Public discovery searches only the public, server-projected collection. */
(() => {
  'use strict';
  const form = document.querySelector('[data-discovery-form]');
  if (!form) return;
  const fields = Object.fromEntries(['q', 'type', 'place', 'date', 'source', 'quality'].map(name => [name, form.elements.namedItem(name)]));
  const records = [...document.querySelectorAll('[data-search-record]')];
  const summary = document.querySelector('[data-summary]');
  const empty = document.querySelector('[data-empty]');
  const copy = document.querySelector('[data-copy]');
  const clean = text => text.toLowerCase().normalize('NFKC').replace(/[^a-z0-9-]+/g, ' ').trim().split(/\s+/).filter(Boolean).map(token => /^0\d$/.test(token) ? token.slice(1) : token);
  const unsupported = /\b(deforestation|forest loss|forest-loss|illegal logging|live alerts?|disturbance alerts?)\b/i;
  const allowed = {type: ['', 'observation', 'place', 'research', 'guide'], place: ['', 'geta'], date: [...fields.date.options].map(option => option.value), source: ['', 'sentinel-2'], quality: ['', 'clearer', 'limited']};
  function restore() {
    const url = new URL(location.href);
    fields.q.value = (url.searchParams.get('q') || '').slice(0, 160);
    for (const name of ['type', 'place', 'date', 'source', 'quality']) {
      const value = url.searchParams.get(name) || '';
      fields[name].value = allowed[name].includes(value) ? value : '';
    }
  }
  function update(write = true) {
    const query = fields.q.value.slice(0, 160).trim();
    const tokens = clean(query);
    const isUnsupported = unsupported.test(query);
    let count = 0;
    for (const record of records) {
      const haystack = clean(record.dataset.search).join(' ');
      const match = !isUnsupported && tokens.every(token => haystack.includes(token)) &&
        (!fields.type.value || record.dataset.kind === fields.type.value) &&
        (!fields.place.value || record.dataset.place === fields.place.value) &&
        (!fields.date.value || record.dataset.date === fields.date.value) &&
        (!fields.source.value || record.dataset.source === fields.source.value) &&
        (!fields.quality.value || record.dataset.quality === fields.quality.value);
      record.hidden = !match;
      if (match) {
        count++;
        let reason = record.querySelector('[data-match-reason]');
        if (!reason) {reason = document.createElement('span'); reason.dataset.matchReason = ''; record.querySelector('[data-why]').prepend(reason);}
        reason.textContent = query ? 'Matched the entered terms and selected filters. ' : 'Included in the selected collection. ';
      }
    }
    summary.textContent = count + (count === 1 ? ' published result' : ' published results');
    empty.hidden = count !== 0;
    empty.textContent = isUnsupported
      ? 'No qualified live forest-loss alert feed is published here. Search coverage or explore the research to understand the evidence and its limits.'
      : 'No published result matches these terms and filters. Try Geta, a date, or clear the filters.';
    if (write) {
      const url = new URL(location.href);
      for (const name of Object.keys(fields)) {
        const value = fields[name].value.trim().slice(0, 160);
        if (value) url.searchParams.set(name, value); else url.searchParams.delete(name);
      }
      history.replaceState(null, '', url.pathname + url.search);
    }
  }
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  form.addEventListener('input', () => update());
  form.addEventListener('change', () => update());
  document.querySelectorAll('[data-suggestion]').forEach(button => button.addEventListener('click', () => {
    fields.q.value = button.dataset.suggestion;
    for (const name of ['type', 'place', 'date', 'source', 'quality']) fields[name].value = '';
    update();
  }));
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    copy.hidden = false;
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(location.href); copy.textContent = 'Link copied'; }
      catch (_) { copy.textContent = 'Copy the URL from your address bar'; }
    });
  }
  window.addEventListener('popstate', () => { restore(); update(false); });
  restore(); update(false); form.hidden = false;
})();
