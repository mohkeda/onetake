# Aggregates Salla order exports covering several months into per-month city and Riyadh-district totals
# (counts and delivery fees per store; no individual orders or locations are kept).
# Usage: python3 aggregate_orders_monthly.py out.json hamtaro=a.xlsx cpstore=b.xlsx wagy=c.xlsx
import openpyxl, re, json, statistics, collections, sys, os, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
CANCEL = re.compile(r'ملغ|محذوف|مسترجع|مرتجع|بإنتظار|بانتظار')
def norm_d(s):
    s = re.sub(r'[ًٌٍَُِّْـ]', '', s).strip()
    s = s.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')
    s = re.sub(r'^(ال)?حي\s+', '', s)
    return re.sub(r'\s+', ' ', s)
def centroid(pts):
    if not pts: return None
    la = statistics.median(p[0] for p in pts); ln = statistics.median(p[1] for p in pts)
    near = [p for p in pts if abs(p[0]-la) < 0.05 and abs(p[1]-ln) < 0.05] or pts
    return [round(sum(p[0] for p in near)/len(near), 2), round(sum(p[1] for p in near)/len(near), 2)]
def fee(v):
    try: return float(v)
    except Exception: return 0.0
def city_ar(en):
    return CITY_AR.get(en, en)
CITY_AR = json.load(open(os.path.join(here, 'city_ar.json'))) if os.path.exists(os.path.join(here, 'city_ar.json')) else {}
out_path, specs = sys.argv[1], dict(a.split('=', 1) for a in sys.argv[2:])
mk = lambda: {'n': collections.Counter(), 'f': collections.Counter(), 'pts': []}
months = collections.defaultdict(lambda: {'cities': collections.defaultdict(mk), 'districts': collections.defaultdict(mk)})
for cid, path in specs.items():
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True); I = {k: i for i, k in enumerate(next(it))}
    for r in it:
        if not r[I['رقم الطلب']] or CANCEL.search(str(r[I['حالة الطلب']])) or str(r[I['يتطلب شحن']]) == 'لا': continue
        mo = str(r[I['تاريخ الطلب']] or '')[:7]
        if not re.match(r'\d{4}-\d{2}$', mo): continue
        M = months[mo]
        city = city_ar(str(r[I['المدينة']] or '').strip() or 'غير محدد')
        m = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', str(r[I['رابط موقع العميل على الخريطة']] or ''))
        lat, lng = (float(m.group(1)), float(m.group(2))) if m else (None, None)
        fe = fee(r[I['تكلفة الشحن']])
        C = M['cities'][city]; C['n'][cid] += 1; C['f'][cid] += fe
        if lat and 16 < lat < 33 and 34 < lng < 56: C['pts'].append((lat, lng))
        if city == 'الرياض':
            dm = re.search(r'(?:حي)\s*[:\-]?\s*([^\-,،\n0-9]+)', str(r[I['عنوان العميل']] or ''))
            if not dm: continue
            D = M['districts'][norm_d(dm.group(1))[:30]]; D['n'][cid] += 1; D['f'][cid] += fe
            if lat and 24.3 < lat < 25.2 and 46.3 < lng < 47.2: D['pts'].append((lat, lng))
pack = lambda name, v: {'name': name, 'n': dict(v['n']), 'f': {k: round(x, 2) for k, x in v['f'].items()}, 'at': centroid(v['pts'])}
out = {}
for mo, M in sorted(months.items()):
    o = {k: sorted((pack(n, v) for n, v in M[k].items()), key=lambda x: -sum(x['n'].values())) for k in ('cities', 'districts')}
    out[mo] = o
    print(mo, {k: len(v) for k, v in o.items()}, {c: sum(x['n'].get(c, 0) for x in o['cities']) for c in specs})
json.dump(out, open(out_path, 'w'), ensure_ascii=False, separators=(',', ':'))
