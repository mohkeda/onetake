import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage(); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(7000);
const out = {};
for (const m of ['2026-08', '2026-09']) {
  await p.evaluate(m => { const s = document.querySelector('#month'); s.value = m; s.dispatchEvent(new Event('change')); }, m);
  await p.waitForTimeout(2500);
  out[m] = await p.evaluate(() => Object.fromEntries(['exhibit','cpstore','hamtaro','wagy','wholesale','main'].map(c => { const s = window.__cpSnapshot(c); const x = s.c[c]; return [c, { revenue: x.revenue, gross: x.gross, net: x.net, netBeforeMgr: x.netBeforeMgr, mgrComm: x.mgrComm||0, tax: x.tax||0, netAfter: x.netAfter, cats: s.cats[c]||{}, matrix: c==='wholesale'? s.ws.matrix : null }]; })));
}
fs.writeFileSync(process.argv[3], JSON.stringify(out));
await b.close();
