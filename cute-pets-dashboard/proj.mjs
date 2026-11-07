import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage(); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(7000);
const out = {};
for (let i = 1; i <= 9; i++) {
  const m = `2026-0${i}`;
  await p.evaluate(m => { const s = document.querySelector('#month'); s.value = m; s.dispatchEvent(new Event('change')); }, m); await p.waitForTimeout(2200);
  out[m] = await p.evaluate(() => Object.fromEntries(['exhibit','cpstore','hamtaro','wagy','wholesale','main'].map(c => { const s = window.__cpSnapshot(c); const x = s.c[c];
    const num = Object.fromEntries(Object.entries(x).filter(([, v]) => typeof v === 'number'));
    return [c, { x: num, lines: x.lines, cats: s.cats[c] || {}, catCost: s.catCost[c] || {}, matrix: c === 'wholesale' ? s.ws.matrix : null, summary: s.summary }]; })));
}
fs.writeFileSync(process.argv[3], JSON.stringify(out)); await b.close();
