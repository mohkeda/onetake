"""Filter the Claude project workbook down to one center, so a center-only project never sees the others.
usage: python3 build_center_project.py <full.xlsx> <center name in Arabic> <out.xlsx> [sheet kept whole …]"""
import sys, openpyxl
src, center, out = sys.argv[1:4]
KEEP = set(sys.argv[4:])
wb = openpyxl.load_workbook(src)
DROP = {'إجمالي الشركة'}
for ws in list(wb.worksheets):
    if ws.title in DROP: wb.remove(ws); continue
    if ws.title in KEEP: continue
    if ws.title in ('ملخص المتاجر',):
        # blocks: title row, header row, center rows, company rows — keep title, header and this center
        keep = [r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value in (center, 'المركز', None) or (ws.cell(r, 2).value is None and ws.cell(r, 1).value)]
    else:
        hdr = [c.value for c in ws[1]]
        col = next((i + 1 for i, h in enumerate(hdr) if h in ('المركز', 'الفرع')), None)
        if not col: continue
        keep = [1] + [r for r in range(2, ws.max_row + 1) if ws.cell(r, col).value == center]
    for r in range(ws.max_row, 0, -1):
        if r not in keep: ws.delete_rows(r)
for ws in list(wb.worksheets):
    if ws.max_row <= 1: wb.remove(ws)   # nothing left for this center
wb.save(out)
print('saved', [w.title for w in wb.worksheets])
