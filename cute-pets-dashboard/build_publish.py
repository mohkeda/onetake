# Bakes real months into a publish-only copy of the dashboard (kept out of the git repo).
import json, sys
src, seed_json, out = sys.argv[1:4]
geo_json = sys.argv[4] if len(sys.argv) > 4 else None   # area totals from aggregate_orders.py (no individual orders)
d = json.load(open(seed_json))
r2 = lambda v: round(v, 2) if isinstance(v, float) else v
compact = {
  'is': {'f': d['is']['fileName'], 'r': [[x['account'], x['center'], r2(x['amount']), x.get('group')] for x in d['is']['rows']]},
  'orders': [{'f': f['fileName'], 'c': f['center'], 'r': [[1 if o['city'] == 'Riyadh' else 0, r2(o['fee']), int(o['cancelled']), int(o['pickup'])] for o in f['rows']]} for f in d['orders']['files']],
  'sales': [{'f': f['fileName'], 'c': f['center'], 'r': [[x['name'], (x.get('brand') or '').strip(), r2(x['qty']), r2(x['sales']), r2(x['bookCost']), x.get('category') or '', x.get('store') or '', 1 if x.get('service') else 0] for x in f['rows']]} for f in d['sales']],
  'payroll': {'f': d['payroll']['fileName'], 'r': [[x['cc'], x['note'], r2(x['cost'])] for x in d['payroll']['rows']]} if d.get('payroll') else None,   # no employee names
  'geo': (lambda g: {'cities': g['cities'], 'districts': g['districts']})(json.load(open(geo_json))) if geo_json else None,
  'cls': d.get('cls') or {},
}
html = open(src, encoding='utf-8').read()
seed = json.dumps({'2026-09': compact}, ensure_ascii=False, separators=(',', ':'))
assert html.count('/*SEED*/null/*END*/') == 1
open(out, 'w', encoding='utf-8').write(html.replace('/*SEED*/null/*END*/', '/*SEED*/' + seed + '/*END*/'))
print('seed bytes', len(seed.encode()))
