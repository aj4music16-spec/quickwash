#!/usr/bin/env python3
"""Builds index.html and compositions/*.html from tools/src/*.html by filling generated snippets:
the real NJ county geometry (tools/nj.json, from us-atlas), 7-segment LED digits, and the shared road background."""
import json, math, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'tools' / 'src'
nj = json.loads((ROOT / 'tools' / 'nj.json').read_text())

# ---- NJ map ---------------------------------------------------------------
cl = nj['pts']['Clifton']
served = [c for c in nj['counties'] if c['served']]
served.sort(key=lambda c: (c['name'] != 'Passaic', math.hypot(c['c'][0] - cl[0], c['c'][1] - cl[1])))  # the pin lands in Passaic County
counties = '\n'.join(
    f'        <path id="cty-{c["id"]}" class="cty {"s" if c["served"] else "u"}" d="{c["d"]}" />'
    for c in sorted(nj['counties'], key=lambda c: c['served']))
order = json.dumps([f'#cty-{c["id"]}' for c in served])

# ---- 7-segment digits -----------------------------------------------------
T = 12
def hseg(x0, y, L): return f'{x0+T/2},{y} {x0+L-T/2},{y} {x0+L},{y+T/2} {x0+L-T/2},{y+T} {x0+T/2},{y+T} {x0},{y+T/2}'
def vseg(x, y0, L): return f'{x+T/2},{y0} {x+T},{y0+T/2} {x+T},{y0+L-T/2} {x+T/2},{y0+L} {x},{y0+L-T/2} {x},{y0+T/2}'
SEG = {'a': hseg(8, 2, 48), 'g': hseg(8, 49, 48), 'd': hseg(8, 96, 48), 'f': vseg(2, 8, 46), 'b': vseg(50, 8, 46), 'e': vseg(2, 55, 46), 'c': vseg(50, 55, 46)}
ON = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abfgcd', 'x': ''}
def dg(v, cls=''):
    polys = ''.join(f'<polygon class="{k}" points="{p}"/>' for k, p in SEG.items())
    return f'<svg class="dg {cls}" data-v="{v}" viewBox="0 0 64 110"><g transform="skewX(-5) translate(5 0)">{polys}</g></svg>'
seg_css = '\n'.join(
    '    ' + ', '.join(f'.dg[data-v="{d}"] .{s}' for d in ON if s in ON[d]) + ' { fill: var(--led, #ffab2e); }'
    for s in 'abcdefg')

# ---- hills ----------------------------------------------------------------
hills_a = 'M0 140 L0 110 ' + ' '.join(f'Q{162*k+81} 44 {162*(k+1)} 110' for k in range(9)) + ' L1458 140 Z'
hills_b = 'M0 150 L0 110 ' + ' '.join(f'Q{324*k+75} 16 {324*k+162} 98 Q{324*k+246} 48 {324*(k+1)} 110' for k in range(5)) + ' L1620 150 Z'

bg_inner = (SRC / '_bg.html').read_text().replace('@@HILLS_A@@', hills_a).replace('@@HILLS_B@@', hills_b)

TOK = {'NJ_COUNTIES': counties, 'NJ_OUTLINE': nj['outline'], 'NJ_ORDER': order, 'SEG_CSS': seg_css, 'BG_INNER': bg_inner,
       'CLIFTON_X': f'{cl[0]:.1f}', 'CLIFTON_Y': f'{cl[1]:.1f}'}

def fill(s):
    for k, v in TOK.items(): s = s.replace(f'@@{k}@@', v)
    s = re.sub(r'@@DG:([0-9x])(?::([\w-]+))?@@', lambda m: dg(m.group(1), m.group(2) or ''), s)
    left = re.findall(r'@@[A-Z_:0-9a-z]+@@', s)
    assert not left, left
    return s

(ROOT / 'index.html').write_text(fill((SRC / 'index.html').read_text()))
(ROOT / 'compositions').mkdir(exist_ok=True)
for f in sorted(SRC.glob('*.html')):
    if f.name in ('index.html', '_bg.html'): continue
    (ROOT / 'compositions' / f.name).write_text(fill(f.read_text()))
    print('wrote compositions/' + f.name)
print('wrote index.html; ripple order:', [c['name'] for c in served])
