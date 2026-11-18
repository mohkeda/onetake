// لوحة نتائج الحيوانات اللطيفة — Google Apps Script
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
