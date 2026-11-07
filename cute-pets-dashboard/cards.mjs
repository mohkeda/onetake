// dump every visible card's tables, per month and per center page: { month: { center|'all': { title: [[cells]] } } }
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1400, height: 900 } }); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(7000);
const dump = () => p.evaluate(() => { const o = {};
  for (const card of document.querySelectorAll('.card')) { if (!card.offsetParent) continue;
    const h = card.querySelector('h2')?.innerText.trim(); if (!h) continue;
    const rows = []; for (const t of card.querySelectorAll('table')) { if (!t.offsetParent) continue; for (const tr of t.querySelectorAll('tr')) rows.push([...tr.children].map(td => td.innerText.trim())); }
    const kp = [...card.querySelectorAll('.kpi')].filter(k => k.offsetParent).map(k => [k.querySelector('.lbl')?.innerText.trim(), k.querySelector('.val')?.innerText.trim(), k.querySelector('.sub')?.innerText.trim()]);
    if (rows.length || kp.length) o[h] = { rows, kpis: kp, note: card.querySelector('.card-head p')?.innerText.trim() || '' }; }
  return o; });
const out = {};
for (const m of process.argv[4].split(',')) {
  await p.evaluate(m => { const s = document.querySelector('#month'); s.value = m; s.dispatchEvent(new Event('change')); }, m); await p.waitForTimeout(2200);
  out[m] = {};
  for (const c of ['all', 'exhibit', 'cpstore', 'hamtaro', 'wagy', 'wholesale']) {
    await p.evaluate(c => { const s = document.querySelector('#centerSel'); s.value = c; s.dispatchEvent(new Event('change')); }, c); await p.waitForTimeout(1800);
    out[m][c] = await dump();
  }
}
fs.writeFileSync(process.argv[3], JSON.stringify(out)); await b.close();
