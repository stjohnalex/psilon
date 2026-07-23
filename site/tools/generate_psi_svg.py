"""Generate the psi logo mark SVG from the Battlestar font's U and I outlines
and patch the three inline copies in site/index.html.

The psi is composed of the font's I (stem) and a reshaped U (bowl): prongs
clamped shorter, bowl widened at its centerline so stroke weight is preserved.
SVG masks cut each letter's stripe gap through the other where they intersect.

Usage: python site/tools/generate_psi_svg.py   (requires fontTools)
"""
import io
import re
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

SITE_DIR = Path(__file__).resolve().parent.parent
FONT = SITE_DIR / "fonts" / "Battlestar.ttf"
HTML = SITE_DIR / "index.html"

# --- design parameters (glyph units, y-up, I baseline at 0, cap 800) ---
U_SCALE = 0.75          # uniform scale keeps U stroke = I stroke after I scaleX
I_SCALEX = 0.75         # slim stem
U_TOP = 660             # U ink top in final units (I top = 800; prongs shorter)
U_BOTTOM = 239          # U ink bottom (bowl bottom on the stem)
U_WIDEN = 107           # extra glyph-units inserted across the bowl (pre-scale)
PAD = 6

font = TTFont(str(FONT))
glyphSet = font.getGlyphSet()
cmap = font.getBestCmap()


def contours(ch):
    pen = RecordingPen()
    glyphSet[cmap[ord(ch)]].draw(pen)
    return pen.value


def u_transform(pt):
    x, y = pt
    # widen: symmetric insert about the bowl center x=362
    if x < 362:
        x -= U_WIDEN / 2
    elif x > 362:
        x += U_WIDEN / 2
    # shorten prongs: clamp the straight top edges down
    if y >= 700:
        y = (U_TOP - U_BOTTOM) / U_SCALE
    x *= U_SCALE
    y = y * U_SCALE + U_BOTTOM
    return x, y


def i_transform(pt):
    x, y = pt
    cx = 213 / 2
    x = cx + (x - cx) * I_SCALEX
    return x, y


def apply(ops, fn):
    return [(op, tuple(fn(p) for p in args)) for op, args in ops]


u_ops = apply(contours("U"), u_transform)
i_ops = apply(contours("I"), i_transform)


def bounds(ops):
    xs = [p[0] for _, args in ops for p in args]
    ys = [p[1] for _, args in ops for p in args]
    return min(xs), min(ys), max(xs), max(ys)


ub = bounds(u_ops)
ib = bounds(i_ops)
u_cx = (ub[0] + ub[2]) / 2
i_cx = (ib[0] + ib[2]) / 2

total_w = ub[2] - ub[0]
CX = total_w / 2 + PAD
TOP_Y = 800 + PAD      # svg y = TOP_Y - y_up


def finalize(ops, cx):
    return [
        (op, tuple((round(CX + (x - cx), 1), round(TOP_Y - y, 1)) for x, y in args))
        for op, args in ops
    ]


u_fin = finalize(u_ops, u_cx)
i_fin = finalize(i_ops, i_cx)

VB_W = round(total_w + 2 * PAD, 1)
VB_H = round(800 + 2 * PAD, 1)


def to_d(ops):
    d = []
    for op, args in ops:
        if op == "moveTo":
            d.append(f"M{args[0][0]} {args[0][1]}")
        elif op == "lineTo":
            d.append(f"L{args[0][0]} {args[0][1]}")
        elif op == "qCurveTo":
            offs, on = list(args)[:-1], args[-1]
            # TrueType implied on-points between consecutive off-points
            segs = []
            for i in range(len(offs) - 1):
                mid = (round((offs[i][0] + offs[i + 1][0]) / 2, 1),
                       round((offs[i][1] + offs[i + 1][1]) / 2, 1))
                segs.append((offs[i], mid))
            segs.append((offs[-1], on))
            for c, e in segs:
                d.append(f"Q{c[0]} {c[1]} {e[0]} {e[1]}")
        elif op == "closePath":
            d.append("Z")
    return "".join(d)


u_d = to_d(u_fin)
i_d = to_d(i_fin)

# --- masks: each letter's stripe gap punches through the other letter ---
# I gap rect: pre-transform x 95..121
g1 = CX + (i_transform((95, 0))[0] - i_cx)
g2 = CX + (i_transform((121, 0))[0] - i_cx)
i_gap_x, i_gap_w = round(g1, 1), round(g2 - g1, 1)

# U bottom gap band: pre-scale y 84..108 above the U's bottom edge
uy1 = TOP_Y - (U_BOTTOM + 108 * U_SCALE)
uy2 = TOP_Y - (U_BOTTOM + 84 * U_SCALE)
u_gap_y, u_gap_h = round(uy1, 1), round(uy2 - uy1, 1)

svg = (
    f'<svg class="glyph psi-svg" viewBox="0 0 {VB_W} {VB_H}" aria-hidden="true">'
    f'<defs>'
    f'<mask id="psiCutU"><rect width="{VB_W}" height="{VB_H}" fill="#fff"/>'
    f'<rect x="{i_gap_x}" y="0" width="{i_gap_w}" height="{VB_H}" fill="#000"/></mask>'
    f'<mask id="psiCutI"><rect width="{VB_W}" height="{VB_H}" fill="#fff"/>'
    f'<rect x="0" y="{u_gap_y}" width="{VB_W}" height="{u_gap_h}" fill="#000"/></mask>'
    f'</defs>'
    f'<path d="{u_d}" fill="currentColor" mask="url(#psiCutU)"/>'
    f'<path d="{i_d}" fill="currentColor" mask="url(#psiCutI)"/>'
    f'</svg>'
)

# --- patch the three inline copies in index.html with per-instance mask ids
# (Chrome fails to resolve mask references across duplicate-id inline SVGs) ---
html = io.open(HTML, encoding="utf-8").read()
suffixes = ["Nav", "Hero", "Foot"]
count = {"i": 0}


def repl(_m):
    sfx = suffixes[count["i"]]
    count["i"] += 1
    return svg.replace("psiCutU", "psiCutU" + sfx).replace("psiCutI", "psiCutI" + sfx)


html = re.sub(r"<svg class=\"glyph psi-svg\".*?</svg>", repl, html, flags=re.S)
io.open(HTML, "w", encoding="utf-8", newline="\n").write(html)
print(f"viewBox 0 0 {VB_W} {VB_H}; patched {count['i']} svg instances in {HTML}")
