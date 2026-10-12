// Builds one report per center from the full (published) dashboard: each output file carries only that
// center's computed results. Usage: node build_center_reports.mjs <full.html> <template index.html> <out dir> [playwright module]
import fs from 'fs';
const [,, full, template, outDir, pwPath = 'playwright'] = process.argv;
const { chromium } = await import(pwPath);
const CENTERS = { exhibit: 'معرض كيوت بيتس', cpstore: 'متجر كيوت بيتس', hamtaro: 'متجر هامتارو', wagy: 'متجر واجي', wholesale: 'الجملة' };
const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const p = await b.newPage();
p.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
await p.goto('file://' + full); await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForTimeout(1500);
const months = await p.evaluate(() => [...new Set(Object.keys(JSON.parse(localStorage.getItem('cutepets-dashboard-v4') || '{}').months || {}))].sort());
const snaps = Object.fromEntries(Object.keys(CENTERS).map(c => [c, {}]));
for (const m of months) {
  await p.evaluate(m => { const el = document.querySelector('#month'); el.value = m; el.dispatchEvent(new Event('change')); }, m);
  await p.waitForTimeout(600);
  if (!await p.evaluate(() => window.__cpSnapshot("exhibit").hasIS)) continue; // month without an income statement
  for (const c of Object.keys(CENTERS)) snaps[c][m] = await p.evaluate(c => window.__cpSnapshot(c), c);
}
await b.close();
const html = fs.readFileSync(template, 'utf8');
if (!html.includes('/*LOCK*/null/*END*/')) throw new Error('template has no LOCK slot');
fs.mkdirSync(outDir, { recursive: true });
for (const [c, name] of Object.entries(CENTERS)) {
  const lock = JSON.stringify({ center: c, months: snaps[c] });
  const out = html.replace('/*LOCK*/null/*END*/', '/*LOCK*/' + lock + '/*END*/').replace(/<title>[^<]*<\/title>/, `<title>تقرير ${name}</title>`);
  fs.writeFileSync(`${outDir}/${c}.html`, out);
  console.log(c, months.join(','), (lock.length / 1024).toFixed(0) + ' KB');
}
