# Bakes real months into a publish-only copy of the dashboard (kept out of the git repo).
import json, sys
src, seed_json, out = sys.argv[1:4]
geo_json = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None   # area totals from aggregate_orders.py (no individual orders)
archive_json = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None   # months closed in the Excel workbook (extract_archive.py)
hist_json = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else None   # parsed monthly sales reports for the archived months
geo_months_json = sys.argv[7] if len(sys.argv) > 7 else None   # per-month city/district totals (aggregate_orders_monthly.py)
d = json.load(open(seed_json))
r2 = lambda v: round(v, 2) if isinstance(v, float) else v
compact = {
  'is': {'f': d['is']['fileName'], 'r': [[x['account'], x['center'], r2(x['amount']), x.get('group')] + ([x['src']] if x.get('src') else []) for x in d['is']['rows']]},
  'orders': [{'f': f['fileName'], 'c': f['center'], 'r': [[1 if o['city'] == 'Riyadh' else 0, r2(o['fee']), int(o['cancelled']), int(o['pickup']), r2(o.get('cod', 0))] for o in f['rows']]} for f in d['orders']['files']],
  'sales': None,
  'payroll': {'f': d['payroll']['fileName'], 'r': [[x['cc'], x['note'], r2(x['cost']), 1 if x.get('doctor') else 0] for x in d['payroll']['rows']], 'emp': d['payroll'].get('emp')} if d.get('payroll') else None,   # no employee names
  'geo': (lambda g: {'cities': g['cities'], 'districts': g['districts']})(json.load(open(geo_json))) if geo_json else None,
  'cls': d.get('cls') or {},
}
html = open(src, encoding='utf-8').read()
def sales_compact(files):
  return [{'f': f['fileName'], 'c': f['center'], 'r': [[x['name'], (x.get('brand') or '').strip(), r2(x['qty']), r2(x['sales']), r2(x['bookCost']), x.get('category') or '', x.get('store') or '', 1 if x.get('service') else 0, x.get('code') or ''] for x in f['rows']]} for f in files]
compact['sales'] = sales_compact(d['sales'])
months = {m: {'archive': a} for m, a in json.load(open(archive_json)).items()} if archive_json else {}
if hist_json:
  for m, h in json.load(open(hist_json)).items():
    if m in months and h.get('sales'): months[m]['sales'] = sales_compact(h['sales']); months[m]['cls'] = h.get('cls') or {}
if geo_months_json:
  for m, g in json.load(open(geo_months_json)).items():
    if m in months and 'archive' in months[m]: months[m]['geo'] = {'cities': g['cities'], 'districts': g['districts']}
months['2026-09'] = compact
seed = json.dumps(months, ensure_ascii=False, separators=(',', ':'))
assert html.count('/*SEED*/null/*END*/') == 1
open(out, 'w', encoding='utf-8').write(html.replace('/*SEED*/null/*END*/', '/*SEED*/' + seed + '/*END*/'))
print('seed bytes', len(seed.encode()))
