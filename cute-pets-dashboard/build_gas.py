"""Builds the Google Apps Script copy of the dashboard: google-apps-script/Index.html + Code.gs.
The page is the same dashboard; its data (closed months, saved results, inputs) lives in one JSON file on the
owner's Google Drive instead of the browser / Claude. Usage: python3 build_gas.py index.html google-apps-script"""
import sys, re
src, out = sys.argv[1:3]
html = open(src, encoding='utf-8').read()
assert html.count('/*SEED*/null/*END*/') == 1
html = html.replace('/*SEED*/null/*END*/', 'window.__CP_SEED || null')
i = html.index('<script>\n(() => {'); j = html.index('</script>', i)
main = html[i + len('<script>'):j]
assert '</script' not in main
LOADER = r'''<div id="cp-boot" style="font-family:system-ui;padding:40px;text-align:center;color:#555">جاري تحميل البيانات…</div>
<script type="text/plain" id="cp-main">''' + main + r'''</script>
<script>
// Google Apps Script host: the data file on Drive is the source of truth; the page keeps working copy in localStorage
(function () {
  var KEY = 'cutepets-dashboard-v4', boot = document.getElementById('cp-boot'), timer = null, pending = null;
  function start() {
    boot.remove();
    var s = document.createElement('script'); s.textContent = document.getElementById('cp-main').textContent; document.body.appendChild(s);
    // every change the dashboard persists is sent to Drive (at most every 3 seconds)
    var set = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function (k, v) {
      set(k, v);
      if (k !== KEY) return;
      pending = v; clearTimeout(timer);
      timer = setTimeout(function () { var p = pending; pending = null; google.script.run.withFailureHandler(function (e) { alert('تعذّر الحفظ على Google Drive: ' + (e && e.message || e)); }).saveStore(p); }, 3000);
    };
    window.addEventListener('beforeunload', function () { if (pending) google.script.run.saveStore(pending); });
  }
  function importScreen(msg) {
    boot.innerHTML = '<h2 style="color:#7a3e12">لوحة نتائج الحيوانات اللطيفة</h2><p>' + (msg || 'لا توجد بيانات بعد. ارفع النسخة الكاملة المصدَّرة من اللوحة على Claude (cutepets-backup-….json).') + '</p><input type="file" id="cp-imp" accept=".json"><p id="cp-st"></p>';
    document.getElementById('cp-imp').onchange = function (e) {
      var f = e.target.files[0]; if (!f) return;
      var fr = new FileReader();
      fr.onload = function () {
        try { var d = JSON.parse(fr.result); if (!d || !d.store) throw new Error('الملف ليس نسخة من اللوحة'); } catch (err) { document.getElementById('cp-st').textContent = err.message; return; }
        document.getElementById('cp-st').textContent = 'جاري الرفع إلى Google Drive…';
        google.script.run.withSuccessHandler(function () { location.reload(); }).withFailureHandler(function (err) { document.getElementById('cp-st').textContent = 'تعذّر الرفع: ' + (err && err.message || err); }).saveAll(fr.result);
      };
      fr.readAsText(f, 'utf-8');
    };
  }
  google.script.run.withSuccessHandler(function (txt) {
    if (!txt) { importScreen(); return; }
    try { var d = JSON.parse(txt); window.__CP_SEED = d.seed || null; localStorage.setItem(KEY, JSON.stringify(d.store || {})); }
    catch (e) { importScreen('ملف البيانات على Drive تالف. ارفع النسخة الكاملة مرة ثانية.'); return; }
    start();
  }).withFailureHandler(function (e) { boot.textContent = 'لا يمكن فتح ملف البيانات: ' + (e && e.message || e) + ' — تأكد أن صاحب اللوحة شارك ملف البيانات معك.'; }).loadData();
})();
</script>'''
html = html[:i] + LOADER + html[j + len('</script>'):]
open(out + '/Index.html', 'w', encoding='utf-8').write(html)
open(out + '/Code.gs', 'w', encoding='utf-8').write(r'''// لوحة نتائج الحيوانات اللطيفة — Google Apps Script
// Deploy: Deploy > New deployment > Web app. Execute as: User accessing the web app. Who has access: Anyone with Google account.
// Access is controlled by the data file on Drive: share «cutepets-dashboard-data.json» with whoever should open the dashboard
// (Editor = can upload and save months, Viewer = can only view).
var FILE_NAME = 'cutepets-dashboard-data.json';

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('لوحة نتائج الحيوانات اللطيفة')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// the data file: its id is kept in the script properties (shared by everyone who opens the web app)
function file_(create) {
  var props = PropertiesService.getScriptProperties(), id = props.getProperty('FILE_ID');
  if (id) return DriveApp.getFileById(id);   // throws for someone the file is not shared with
  if (!create) return null;
  var f = DriveApp.createFile(FILE_NAME, '', 'application/json');
  props.setProperty('FILE_ID', f.getId());
  return f;
}

function loadData() {
  var f = file_(false);
  return f ? f.getBlob().getDataAsString('UTF-8') : '';
}

// the full backup exported from the Claude dashboard (closed months + saved results + inputs)
function saveAll(json) {
  var d = JSON.parse(json);
  if (!d || !d.store) throw new Error('الملف ليس نسخة من اللوحة');
  file_(true).setContent(JSON.stringify({ v: 1, at: new Date().toISOString(), seed: d.seed || null, store: d.store }));
  return true;
}

// the dashboard's saved state, after every change
function saveStore(storeJson) {
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var f = file_(true), txt = f.getBlob().getDataAsString('UTF-8'), d = txt ? JSON.parse(txt) : { v: 1, seed: null };
    d.store = JSON.parse(storeJson); d.at = new Date().toISOString(); d.by = Session.getActiveUser().getEmail();
    f.setContent(JSON.stringify(d));
    return true;
  } finally { lock.releaseLock(); }
}
''')
print('Index.html', round(len(html.encode()) / 1024), 'KB')
