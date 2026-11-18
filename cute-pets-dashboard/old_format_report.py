"""Monthly results report in the format of the old monthly Excel workbook (النتائج الشهريه), as a printable HTML page:
1) income statement with % of revenue and % of expenses, 2) categories by month + clustered bars, 3) category pie, 4) colored summary box.
Usage: python3 old_format_report.py data.json out.html   then print to PDF (Chromium, A4).
data.json: {TITLE, REV:[[label,amount]], ADM:[...], OPX:[...], TAX, MONTHS:[...], CATS:[[name,[per month]]]}
The data files hold the business's figures: keep them out of the (public) repository."""
import math, json, sys
D = json.load(open(sys.argv[1], encoding='utf-8'))
TITLE, REV, ADM, OPX, TAX, MONTHS, CATS = (D[k] for k in ('TITLE', 'REV', 'ADM', 'OPX', 'TAX', 'MONTHS', 'CATS'))
rev = sum(v for _,v in REV); adm = sum(v for _,v in ADM); opx = sum(v for _,v in OPX); exp = adm + opx; net = rev - exp
f = lambda v: f'{v:,.2f}'
p = lambda v, b: f'{v / b * 100:.2f}%' if b else ''
# page 1: income statement
rows = f'<tr class="t"><td class="n b">{f(net)}</td><td colspan="3" class="b c" style="direction:rtl">{TITLE}</td></tr>'
rows += '<tr class="h"><td></td><td></td><td class="b">المبلغ</td><td class="b">البيان</td></tr>'
rows += f'<tr class="s"><td class="n b">{f(rev)}</td><td></td><td></td><td class="b">أولا الإيرادات</td></tr>'
for l, v in REV: rows += f'<tr><td></td><td class="n">{p(v, rev)}</td><td class="n">{f(v)}</td><td>{l}</td></tr>'
rows += f'<tr class="s"><td></td><td class="n b">100.00%</td><td class="n b">{f(rev)}</td><td class="b">الإجمالي</td></tr>'
rows += f'<tr class="s"><td class="n b">{f(exp)}</td><td></td><td></td><td class="b">ثانيا المصروفات</td></tr>'
rows += f'<tr class="s"><td class="n b">{f(adm)}</td><td></td><td></td><td class="b">المصاريف الاداريه</td></tr>'
for l, v in ADM: rows += f'<tr><td class="n">{p(v, rev)}</td><td class="n">{p(v, exp)}</td><td class="n">{f(v)}</td><td>{l}</td></tr>'
rows += f'<tr class="s"><td class="n b">{f(opx)}</td><td></td><td></td><td class="b">المصاريف التشغيليه</td></tr>'
for l, v in OPX: rows += f'<tr><td class="n">{p(v, rev)}</td><td class="n">{p(v, exp)}</td><td class="n">{f(v)}</td><td>{l}</td></tr>'
rows += f'<tr class="s"><td class="n b">{p(exp, rev)}</td><td class="n b">100.00%</td><td class="n b">{f(exp)}</td><td class="b">إجمالي المصروفات</td></tr>'
rows += f'<tr class="g"><td class="n b">{p(net, rev)}</td><td></td><td class="n b">{f(net)}</td><td class="b">صافي الربح / الخسارة</td></tr>'
rows += f'<tr><td class="n">{p(-TAX, rev)}</td><td></td><td class="n">{f(-TAX)}</td><td>ضريبة الدخل (مساهمة المحل)</td></tr>'
rows += f'<tr class="g"><td class="n b">{p(net - TAX, rev)}</td><td></td><td class="n b">{f(net - TAX)}</td><td class="b">صافي الربح بعد الضريبة</td></tr>'
page1 = f'<table class="x is">{rows}</table>'
# page 2: categories by month + clustered bars
tot = [sum(c[1][i] for c in CATS) for i in range(len(MONTHS))]
crow = '<tr class="h"><td class="b">التصنيف</td>' + ''.join(f'<td class="b">{m}</td>' for m in MONTHS) + '</tr>'
for nm, vs in CATS: crow += f'<tr><td>{nm}</td>' + ''.join(f'<td class="n">{f(v)}</td>' for v in vs) + '</tr>'
crow += '<tr class="s"><td class="b">الإجمالي</td>' + ''.join(f'<td class="n b">{f(v)}</td>' for v in tot) + '</tr>'
COL = ['#4f81bd', '#c0504d', '#9bbb59', '#8064a2', '#4bacc6']
W, H, L, B = 1000, 430, 70, 120; mx = 80000; n = len(CATS); gw = (W - L - 20) / n; bw = gw * 0.8 / len(MONTHS)
svg = f'<svg viewBox="0 0 {W} {H}" width="100%" style="background:#3a3a3a"><text x="{W/2}" y="22" fill="#fff" font-size="15" text-anchor="middle" font-weight="700">مبيعات التصنيفات شهر بشهر</text>'
for k in range(0, 9):
    y = H - B - (H - B - 40) * k * 10000 / mx
    svg += f'<line x1="{L}" x2="{W-20}" y1="{y:.1f}" y2="{y:.1f}" stroke="#666" stroke-width="0.6"/><text x="{L-6}" y="{y+4:.1f}" fill="#ddd" font-size="10" text-anchor="end">{k*10000:,}</text>'
for i, (nm, vs) in enumerate(CATS):
    x0 = W - 20 - (i + 1) * gw + gw * 0.1
    for j, v in enumerate(vs):
        h = (H - B - 40) * v / mx; svg += f'<rect x="{x0 + j*bw:.1f}" y="{H-B-h:.1f}" width="{bw-0.5:.1f}" height="{h:.1f}" fill="{COL[j]}"/>'
    svg += f'<text transform="translate({x0 + gw*0.4:.1f},{H-B+8}) rotate(-60)" fill="#fff" font-size="10" text-anchor="start">{nm}</text>'
for j, m in enumerate(MONTHS):
    svg += f'<rect x="{W/2 + 150 - j*75}" y="{H-18}" width="10" height="10" fill="{COL[j]}"/><text x="{W/2 + 145 - j*75}" y="{H-9}" fill="#fff" font-size="11" text-anchor="end">{m}</text>'
svg += '</svg>'
page2 = f'<table class="x cat">{crow}</table><div style="margin-top:14px">{svg}</div>'
# page 3: pie of October shares
oc = sorted(((nm, vs[-1]) for nm, vs in CATS), key=lambda t: -t[1]); ot = sum(v for _, v in oc)
PC = ['#9bbb59','#8064a2','#4bacc6','#f79646','#4f81bd','#c0504d','#2c4d75','#772c2a','#5f7530','#4d3b62','#276a7c','#b65708','#729aca','#cd7371','#afc97a','#a491c0','#6fbdd3','#f9ab6b','#3b6596','#9e4a48']
cx, cy, r = 400, 330, 230; a0 = -math.pi / 2; pie = '<svg viewBox="0 0 800 700" width="100%"><text x="400" y="40" text-anchor="middle" font-size="20" font-weight="700">حصص التصنيفات — ' + MONTHS[-1] + '</text>'
for k, (nm, v) in enumerate(oc):
    a1 = a0 + 2 * math.pi * v / ot; big = 1 if a1 - a0 > math.pi else 0
    pie += f'<path d="M{cx},{cy} L{cx + r*math.cos(a0):.1f},{cy + r*math.sin(a0):.1f} A{r},{r} 0 {big} 1 {cx + r*math.cos(a1):.1f},{cy + r*math.sin(a1):.1f} Z" fill="{PC[k % len(PC)]}" stroke="#fff" stroke-width="1"/>'
    am = (a0 + a1) / 2; share = v / ot * 100
    if share >= 1.2:
        rr = r + 34 if share < 6 else r * 0.62; col = '#222' if share < 6 else '#fff'
        pie += f'<text x="{cx + rr*math.cos(am):.1f}" y="{cy + rr*math.sin(am):.1f}" font-size="{12 if share < 6 else 14}" text-anchor="middle" fill="{col}">{nm}</text><text x="{cx + rr*math.cos(am):.1f}" y="{cy + rr*math.sin(am) + 15:.1f}" font-size="12" text-anchor="middle" fill="{col}">{share:.1f}%</text>'
    a0 = a1
pie += '</svg>'
small = '، '.join(f'{nm} {v / ot * 100:.1f}%' for nm, v in oc if v / ot * 100 < 1.2)
page3 = f'<div class="pie">{pie}<p style="font-size:11px;color:#555;text-align:center">أقل من 1.2%: {small}</p></div>'
# page 4: summary box
srows = '<tr class="h"><td class="b">المبلغ</td><td class="b">البيان</td></tr>'
for l, v in REV: srows += f'<tr class="lg"><td class="n">{f(v)}</td><td>{l}</td></tr>'
srows += f'<tr class="gr"><td class="n b">{f(rev)}</td><td class="b">اجمالي الايرادات</td></tr>'
srows += f'<tr class="or"><td class="n b">{f(adm)}</td><td class="b">المصاريف الاداريه</td></tr>'
srows += f'<tr class="or"><td class="n b">{f(opx)}</td><td class="b">المصاريف التشغيليه</td></tr>'
srows += f'<tr class="rd"><td class="n b">{f(exp)}</td><td class="b">اجمالي المصاريف</td></tr>'
srows += f'<tr class="pu"><td class="n b">{f(net)}</td><td class="b">صافي الربح أو الخساره</td></tr>'
srows += f'<tr class="pu"><td class="n b">{f(net - TAX)}</td><td class="b">صافي الربح بعد الضريبة</td></tr>'
page4 = f'<table class="x sum">{srows}</table>'
css = '''@page{size:A4;margin:12mm}body{font-family:Calibri,"Noto Naskh Arabic","DejaVu Sans",Arial,sans-serif;font-size:11px;direction:rtl;color:#000}
.pg{page-break-after:always}.pg:last-child{page-break-after:auto}
table.x{border-collapse:collapse;margin:0 auto}table.is,table.sum{direction:ltr}table.is td:last-child,table.sum td:last-child{text-align:right;direction:rtl}table.x td{border:1px solid #000;padding:2px 6px;white-space:nowrap}
table.is{width:62%;font-size:10px}table.is td{padding:1px 6px}table.is td:nth-child(1),table.is td:nth-child(2),table.is td:nth-child(3){text-align:left;width:14%}
table.cat{width:96%}table.cat td{text-align:left}table.cat td:first-child{text-align:right}
td.n{text-align:left;direction:ltr}td.b{font-weight:700}td.c{text-align:center}
tr.t td{background:#fff;font-size:12px}tr.h td{background:#f2f2f2}tr.s td{background:#f2f2f2}tr.g td{background:#d9ead3}
table.sum{width:46%;margin-top:30px;font-size:13px}table.sum td{padding:4px 8px}
tr.lg td{background:#ebf1de}tr.gr td{background:#92d050}tr.or td{background:#fac090}tr.rd td{background:#ff0000;color:#fff}tr.pu td{background:#7f5fa0;color:#fff}
.pie{border:1px solid #999;width:70%;margin:20px auto;padding:6px}'''
html = f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body><div class="pg">{page1}</div><div class="pg">{page2}</div><div class="pg">{page3}</div><div class="pg">{page4}</div></body></html>'
open(sys.argv[2], 'w', encoding='utf-8').write(html)
print('rev', round(rev, 2), 'adm', round(adm, 2), 'opx', round(opx, 2), 'net', round(net, 2), 'cats oct', ot)
