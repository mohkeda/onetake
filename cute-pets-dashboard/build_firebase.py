"""Builds the Firebase Hosting copy of the dashboard into firebase/public (+ firebase.json, firestore.rules).
Same interactive dashboard; sign-in with Google; the data (closed months, saved results, inputs) lives in Firestore,
split into ~700 KB chunks (a Firestore document holds at most 1 MiB).
Usage: python3 build_firebase.py index.html firebase firebase-config.json
firebase-config.json = the firebaseConfig object from the Firebase console (not secret)."""
import sys, json, os
src, out, cfg_path = sys.argv[1:4]
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {"apiKey": "REPLACE", "authDomain": "REPLACE", "projectId": "REPLACE", "appId": "REPLACE"}
html = open(src, encoding='utf-8').read()
assert html.count('/*SEED*/null/*END*/') == 1
html = html.replace('/*SEED*/null/*END*/', 'window.__CP_SEED || null')
i = html.index('<script>\n(() => {'); j = html.index('</script>', i)
main = html[i + len('<script>'):j]
LOADER = r'''<div id="cp-boot" dir="rtl" style="position:fixed;inset:0;z-index:2147483000;background:#faf8f5;overflow:auto;font-family:system-ui;padding:80px 20px;text-align:center;color:#555">جاري التحميل…</div>
<script type="text/plain" id="cp-main">''' + main + r'''</script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>
<script>
(function () {
  firebase.initializeApp(''' + json.dumps(cfg) + r''');
  var auth = firebase.auth(), db = firebase.firestore(), KEY = 'cutepets-dashboard-v4', CH = 700000;
  var boot = document.getElementById('cp-boot'), timer = null, pending = null, started = false;
  function put(name, txt) {   // a long JSON string in chunks: dash/{name} = {n}, dash/{name}_0 … dash/{name}_{n-1} = {t}
    var b = db.batch(), n = Math.ceil(txt.length / CH) || 1;
    for (var k = 0; k < n; k++) b.set(db.collection('dash').doc(name + '_' + k), { t: txt.slice(k * CH, (k + 1) * CH) });
    b.set(db.collection('dash').doc(name), { n: n, at: new Date().toISOString(), by: auth.currentUser.email });
    return b.commit();
  }
  function get(name) {
    return db.collection('dash').doc(name).get().then(function (m) {
      if (!m.exists) return null;
      var ps = []; for (var k = 0; k < m.data().n; k++) ps.push(db.collection('dash').doc(name + '_' + k).get());
      return Promise.all(ps).then(function (ds) { return ds.map(function (d) { return d.data().t; }).join(''); });
    });
  }
  function start() {
    started = true; boot.remove();
    var s = document.createElement('script'); s.textContent = document.getElementById('cp-main').textContent; document.body.appendChild(s);
    var set = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function (k, v) {
      try { set(k, v); } catch (e) {}
      if (k !== KEY) return;
      pending = v; clearTimeout(timer);
      timer = setTimeout(function () { var p = pending; pending = null; put('store', p).catch(function (e) { alert('تعذّر الحفظ: ' + e.message); }); }, 4000);
    };
    window.addEventListener('beforeunload', function () { if (pending) put('store', pending); });
    var bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;bottom:8px;left:8px;font:12px system-ui;color:#666;background:#fff;border:1px solid #ddd;border-radius:8px;padding:4px 8px;z-index:99';
    bar.innerHTML = auth.currentUser.email + ' · <a href="#" id="cp-out">خروج</a>'; document.body.appendChild(bar);
    document.getElementById('cp-out').onclick = function (e) { e.preventDefault(); auth.signOut().then(function () { location.reload(); }); };
  }
  function importScreen() {
    boot.innerHTML = '<h2 style="color:#7a3e12">لوحة نتائج الحيوانات اللطيفة</h2><p>لا توجد بيانات بعد. ارفع النسخة الكاملة المصدَّرة من اللوحة على Claude (cutepets-backup-….json).</p><input type="file" id="cp-imp" accept=".json"><p id="cp-st"></p>';
    document.getElementById('cp-imp').onchange = function (e) {
      var f = e.target.files[0]; if (!f) return; var fr = new FileReader(), st = document.getElementById('cp-st');
      fr.onload = function () {
        var d; try { d = JSON.parse(fr.result); if (!d || !d.store) throw new Error('الملف ليس نسخة من اللوحة'); } catch (err) { st.textContent = err.message; return; }
        st.textContent = 'جاري الرفع…';
        put('seed', JSON.stringify(d.seed || null)).then(function () { return put('store', JSON.stringify(d.store)); })
          .then(function () { location.reload(); }, function (err) { st.textContent = 'تعذّر الرفع: ' + err.message; });
      };
      fr.readAsText(f, 'utf-8');
    };
  }
  function load() {
    boot.textContent = 'جاري تحميل البيانات…';
    Promise.all([get('seed'), get('store')]).then(function (r) {
      if (!r[1]) { importScreen(); return; }
      window.__CP_SEED = r[0] ? JSON.parse(r[0]) : null;
      try { localStorage.setItem(KEY, r[1]); } catch (e) { window.__CP_STORE = r[1]; }
      start();
    }, function (e) {
      boot.innerHTML = 'غير مصرح لهذا الحساب (' + auth.currentUser.email + ') بفتح اللوحة.<br><br><a href="#" id="cp-out2">تسجيل الدخول بحساب آخر</a>';
      document.getElementById('cp-out2').onclick = function (ev) { ev.preventDefault(); auth.signOut().then(function () { location.reload(); }); };
    });
  }
  auth.onAuthStateChanged(function (u) {
    if (started) return;
    if (u) { load(); return; }
    boot.innerHTML = '<h2 style="color:#7a3e12">لوحة نتائج الحيوانات اللطيفة</h2><button id="cp-in" style="font-size:16px;padding:10px 18px">تسجيل الدخول بحساب جوجل</button>';
    document.getElementById('cp-in').onclick = function () { auth.signInWithPopup(new firebase.auth.GoogleAuthProvider()).catch(function (e) { alert(e.message); }); };
  });
})();
</script>'''
html = html[:i] + LOADER + html[j + len('</script>'):]
# localStorage blocked: the store comes from memory
html = html.replace("JSON.parse(localStorage.getItem(LS_KEY) || 'null')", "JSON.parse(window.__CP_STORE || localStorage.getItem(LS_KEY) || 'null')", 1)
os.makedirs(out + '/public', exist_ok=True)
open(out + '/public/index.html', 'w', encoding='utf-8').write(html)
json.dump({"hosting": {"public": "public", "ignore": ["firebase.json", "**/.*"], "headers": [{"source": "**", "headers": [{"key": "Cache-Control", "value": "no-cache"}, {"key": "X-Robots-Tag", "value": "noindex"}]}]},
           "firestore": {"rules": "firestore.rules"}}, open(out + '/firebase.json', 'w'), indent=2)
if not os.path.exists(out + '/firestore.rules'):
    open(out + '/firestore.rules', 'w').write('''rules_version = '2';
// Who may open the dashboard: put the Google e-mails here (editors upload and save; viewers only look).
service cloud.firestore {
  match /databases/{database}/documents {
    function editors() { return ['OWNER@gmail.com']; }
    function viewers() { return editors().concat([]); }
    function signedIn() { return request.auth != null && request.auth.token.email_verified == true; }
    match /dash/{doc} {
      allow read: if signedIn() && request.auth.token.email in viewers();
      allow write: if signedIn() && request.auth.token.email in editors();
    }
  }
}
''')
print('index.html', round(len(html.encode()) / 1024), 'KB', '· config', 'set' if cfg['apiKey'] != 'REPLACE' else 'placeholder')
