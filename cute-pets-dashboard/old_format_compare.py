import sys, re
"""Two months side by side in the old workbook format, with the differences and a profit bridge.
Usage: python3 old_format_compare.py earlier.json later.json out.html  (same data files as old_format_report.py)"""
import json
S = json.load(open(sys.argv[1], encoding='utf-8')); O = json.load(open(sys.argv[2], encoding='utf-8'))
f = lambda v: f'{v:,.2f}'
def pct(a, b): return f'{a / b * 100:.2f}%' if b else ''
def merge(a, b):
    keys = [k for k, _ in a] + [k for k, _ in b if k not in dict(a)]
    da, db = dict(a), dict(b); return [(k, da.get(k, 0), db.get(k, 0)) for k in keys]
# align labels that differ slightly between the two months
REV = merge(S['REV'], O['REV']); ADM = merge(S['ADM'], O['ADM']); OPX = merge(S['OPX'], O['OPX'])
def tot(L, i): return sum(x[i] for x in L)
rS, rO = tot(REV, 1), tot(REV, 2); aS, aO = tot(ADM, 1), tot(ADM, 2); oS, oO = tot(OPX, 1), tot(OPX, 2)
eS, eO = aS + oS, aO + oO; nS, nO = rS - eS, rO - eO
def d(sep, oct_, cost=False):
    x = oct_ - sep
    if abs(x) < 0.005: return '<td class="n">—</td><td class="n"></td>'
    good = (x < 0) if cost else (x > 0)
    cls = 'up' if good else 'dn'
    return f'<td class="n {cls}">{f(x)}</td><td class="n {cls}">{(x / abs(sep) * 100):+.1f}%</td>' if sep else f'<td class="n {cls}">{f(x)}</td><td class="n {cls}">جديد</td>'
H = '<tr class="h"><td class="b">% الفرق</td><td class="b">الفرق</td><td class="b">% من الإيرادات</td><td class="b">شهر 10</td><td class="b">% من الإيرادات</td><td class="b">شهر 9</td><td class="b">البيان</td></tr>'
def line(l, a, b, base_a, base_b, cost=False, cls=''):
    return f'<tr class="{cls}">' + d(a, b, cost) + f'<td class="n">{pct(b, base_b)}</td><td class="n">{f(b)}</td><td class="n">{pct(a, base_a)}</td><td class="n">{f(a)}</td><td>{l}</td></tr>'
rows = f'<tr class="t"><td colspan="7" class="b c" style="direction:rtl">مقارنة النتائج الشهريه للمحل (معرض كيوت بيتس) — ' + S['MONTHS'][-1] + ' و' + O['MONTHS'][-1] + ' / 2026</td></tr>' + H
rows += '<tr class="s"><td colspan="6"></td><td class="b">أولا الإيرادات</td></tr>'
for l, a, b in REV: rows += line(l, a, b, rS, rO)
rows += line('إجمالي الإيرادات', rS, rO, rS, rO, cls='s b')
rows += '<tr class="s"><td colspan="6"></td><td class="b">ثانيا المصروفات</td></tr>'
rows += line('المصاريف الاداريه', aS, aO, rS, rO, True, 's b')
for l, a, b in ADM: rows += line(l, a, b, rS, rO, True)
rows += line('المصاريف التشغيليه', oS, oO, rS, rO, True, 's b')
for l, a, b in OPX: rows += line(l, a, b, rS, rO, True)
rows += line('إجمالي المصروفات', eS, eO, rS, rO, True, 's b')
rows += line('صافي الربح / الخسارة', nS, nO, rS, rO, cls='g b')
rows += line('ضريبة الدخل', S['TAX'], O['TAX'], rS, rO, True)
rows += line('صافي الربح بعد الضريبة', nS - S['TAX'], nO - O['TAX'], rS, rO, cls='g b')
page1 = f'<table class="x is">{rows}</table>'
# bridge: where the profit difference comes from
gS = rS - (dict((k, a) for k, a, b in OPX)['تكلفة البضاعه المباعه'] + dict((k, a) for k, a, b in OPX)['تكلفه بضاعه الجملة'])
gO = rO - (dict((k, b) for k, a, b in OPX)['تكلفة البضاعه المباعه'] + dict((k, b) for k, a, b in OPX)['تكلفه بضاعه الجملة'])
items = [(l, (b - a) if l in [x[0] for x in REV] else -(b - a)) for l, a, b in REV + ADM + OPX]
items = [(l, v) for l, v in items if abs(v) >= 0.5]
items.sort(key=lambda t: -abs(t[1]))
br = '<tr class="h"><td class="b">التراكمي</td><td class="b">الأثر على الربح</td><td class="b">البند</td></tr>'
run = 0
for l, v in items:
    run += v; cls = 'up' if v > 0 else 'dn'
    br += f'<tr><td class="n">{f(run)}</td><td class="n {cls}">{f(v)}</td><td>{l}</td></tr>'
br += f'<tr class="g"><td class="n b">{f(nO - nS)}</td><td class="n b">{f(nO - nS)}</td><td class="b">إجمالي فرق صافي الربح</td></tr>'
page2 = f'<h3>من وين جا فرق الربحيه (شهر 10 مقابل شهر 9)</h3><p class="note">كل بند وأثره على صافي الربح: الموجب زوّد الربح والسالب نقّصه، مرتبة من الأكبر أثراً. الإيرادات زيادتها موجبة، والمصاريف نزولها موجب.</p><table class="x br">{br}</table>'
# summary box like the old sheet, two months + difference
def srow(l, a, b, cls, cost=False): return f'<tr class="{cls}">' + d(a, b, cost) + f'<td class="n b">{f(b)}</td><td class="n b">{f(a)}</td><td class="b">{l}</td></tr>'
sm = '<tr class="h"><td class="b">% الفرق</td><td class="b">الفرق</td><td class="b">شهر 10</td><td class="b">شهر 9</td><td class="b">البيان</td></tr>'
sm += srow('اجمالي الايرادات', rS, rO, 'gr') + srow('مجمل الربح (بعد تكلفة البضاعه)', gS, gO, 'lg') + srow('المصاريف الاداريه', aS, aO, 'or', True) + srow('المصاريف التشغيليه (بدون تكلفة البضاعه)', oS - (rS - gS), oO - (rO - gO), 'or', True) + srow('اجمالي المصاريف', eS, eO, 'rd', True) + srow('صافي الربح أو الخساره', nS, nO, 'pu') + srow('صافي الربح بعد الضريبة', nS - S['TAX'], nO - O['TAX'], 'pu')
sm += f'<tr><td colspan="2"></td><td class="n">{pct(nO, rO)}</td><td class="n">{pct(nS, rS)}</td><td>هامش صافي الربح</td></tr>'
sm += f'<tr><td colspan="2"></td><td class="n">{pct(gO, rO)}</td><td class="n">{pct(gS, rS)}</td><td>هامش مجمل الربح</td></tr>'
page2 = f'<h3>الملخص</h3><table class="x sum">{sm}</table>' + page2
# categories
cs = dict(S['CATS']); co = dict(O['CATS'])
names = [n for n, _ in O['CATS']] + [n for n in cs if n not in co]
cr = '<tr class="h"><td class="b">% الفرق</td><td class="b">الفرق</td><td class="b">شهر 10</td><td class="b">شهر 9</td><td class="b">التصنيف</td></tr>'
ts = to = 0
for n in names:
    a = cs.get(n, [0])[-1]; b = co.get(n, [0])[-1]; ts += a; to += b
    cr += '<tr>' + d(a, b) + f'<td class="n">{f(b)}</td><td class="n">{f(a)}</td><td>{n}</td></tr>'
cr += '<tr class="s">' + d(ts, to) + f'<td class="n b">{f(to)}</td><td class="n b">{f(ts)}</td><td class="b">الإجمالي</td></tr>'
page3 = f'<h3>مبيعات التصنيفات — شهر 9 مقابل شهر 10</h3><table class="x cat">{cr}</table>'
css = '''@page{size:A4;margin:10mm}body{font-family:Calibri,"Noto Naskh Arabic","DejaVu Sans",Arial,sans-serif;font-size:10px;color:#000}
.pg{page-break-after:always;direction:rtl}.pg:last-child{page-break-after:auto}h3{text-align:center;margin:6px 0}.note{text-align:center;color:#555;font-size:10px;margin:2px 0 6px}
table.x{border-collapse:collapse;margin:0 auto;direction:ltr}table.x td{border:1px solid #000;padding:1px 5px;white-space:nowrap;text-align:left}
table.x td:last-child{text-align:right;direction:rtl}table.is{width:96%}table.br{width:70%}table.sum{width:80%;font-size:11px}table.sum td{padding:3px 6px}table.cat{width:75%}
td.n{direction:ltr}td.b,tr.b td{font-weight:700}td.c{text-align:center!important}.up{color:#006100;background:#c6efce}.dn{color:#9c0006;background:#ffc7ce}
tr.h td{background:#f2f2f2;font-weight:700;text-align:center}tr.s td{background:#f2f2f2}tr.g td{background:#d9ead3}tr.t td{font-size:12px}
tr.lg td{background:#ebf1de}tr.gr td{background:#92d050}tr.or td{background:#fac090}tr.rd td{background:#ff0000;color:#fff}tr.pu td{background:#7f5fa0;color:#fff}
tr.gr td.up,tr.lg td.up,tr.or td.up,tr.rd td.up,tr.pu td.up{background:#c6efce;color:#006100}tr.gr td.dn,tr.lg td.dn,tr.or td.dn,tr.rd td.dn,tr.pu td.dn{background:#ffc7ce;color:#9c0006}'''
html = f'<!DOCTYPE html><html lang="ar"><head><meta charset="utf-8"><style>{css}</style></head><body><div class="pg">{page1}</div><div class="pg">{page2}</div><div class="pg">{page3}</div></body></html>'
html = html.replace('شهر 10', '\x01').replace('شهر 9', S['MONTHS'][-1]).replace('\x01', O['MONTHS'][-1])
open(sys.argv[3], 'w', encoding='utf-8').write(html)
print('rev', rS, rO, 'net', round(nS, 2), round(nO, 2), 'diff', round(nO - nS, 2), 'bridge', round(sum(v for _, v in items), 2))
