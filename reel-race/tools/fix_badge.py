"""Correct the client's WashClub badge: the two "8" (in "8%") become "5" (the rate is 5%). Only those two glyphs change.
Usage: python3 -I tools/fix_badge.py assets/app/washclub-badge.png assets/app/washclub-badge-5.png <fonts dir> [font file]
(used: ... tools/fonts Poppins-Bold.ttf - the closest stroke weight by eye; SemiBold scored best on the 8 shape alone. Candidate
fonts: Google Fonts OFL files, Quicksand, Nunito, Poppins, Fredoka, Baloo 2, Varela Round.)
For each 8: measure its white ink box; fit candidate rounded bold fonts by rendering "8" scaled to that exact box and
scoring the pixel error against the original (the closest face also matches the neighbouring "%"); paint the 8 out with a
Coons-patch fill interpolated from the navy just outside its box (rows and columns), then set "5" in the winning face at the
same height, baseline and centre, with the badge's thin dark-navy edge, rendered 8x and downsampled for matching anti-aliasing."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
SRC, DST, FD = sys.argv[1:4]
im = Image.open(SRC).convert("RGBA"); A = np.asarray(im).astype(float)
SPOTS = {"icon": (849, 435, 884, 480), "line": (978, 436, 1001, 464)}     # white ink boxes of the two 8s (x0, y0, x1, y1)
FONTS = [("Quicksand", "Quicksand.ttf", w) for w in (600, 700)] + [("Nunito", "Nunito.ttf", w) for w in (800, 900)] + \
        [("Poppins", "Poppins-SemiBold.ttf", None), ("Poppins", "Poppins-Bold.ttf", None)] + [("Fredoka", "Fredoka.ttf", w) for w in (500, 600)] + \
        [("Baloo2", "Baloo2.ttf", w) for w in (600, 700, 800)] + [("VarelaRound", "VarelaRound-Regular.ttf", None)]
SS = 8

def face(path, w, size):
    f = ImageFont.truetype(os.path.join(FD, path), size)
    if w is not None:
        try:
            axes = f.get_variation_axes(); f.set_variation_by_axes([w if a.get("name", b"") in (b"Weight", "Weight") else a["default"] for a in axes])
        except Exception:
            f.set_variation_by_axes([w])
    return f

def glyph_mask(ch, path, w, box):
    """white mask of `ch` scaled so its ink box is exactly `box`, with the glyph's own box returned at 8x"""
    f = face(path, w, 400); l, t, r, b = f.getbbox(ch)
    g = Image.new("L", (r - l + 40, b - t + 40), 0); ImageDraw.Draw(g).text((20 - l, 20 - t), ch, font=f, fill=255)
    g = g.crop(g.getbbox()); bw, bh = box[2] - box[0], box[3] - box[1]
    return np.asarray(g.resize((bw, bh), Image.LANCZOS)).astype(float) / 255, (r - l) / (b - t)

def whiteness(x0, y0, x1, y1):
    r = A[y0:y1, x0:x1, :3]; return np.clip((r.min(axis=2) - 40) / (235 - 40), 0, 1)

scores = {}
for name, path, w in FONTS:
    tot = 0
    for spot, box in SPOTS.items():
        m, _ = glyph_mask("8", path, w, box); tot += np.abs(m - whiteness(*box)).mean()
    scores[(name, path, w)] = tot / len(SPOTS)
best = min(scores, key=scores.get)
if len(sys.argv) > 4: best = next(k for k in scores if k[1] == sys.argv[4])   # optional override: the font file to use
for k, v in sorted(scores.items(), key=lambda kv: kv[1]): print(f"{k[0]:12s} {str(k[2] or ''):4s} err {v:.4f}")
print("best:", best)

def navy_fill(x0, y0, x1, y1):
    """each row's background navy: the median of the plain-navy pixels (no white type, no orange, no cyan bubble) within
    25 px either side of the box on that row; the rows are then lightly smoothed vertically"""
    rows = []
    for y in range(y0, y1):
        seg = np.r_[A[y, x0 - 25:x0, :3], A[y, x1:x1 + 25, :3]]
        ok = seg[(seg[:, 0] < 40) & (seg[:, 1] < 60) & (seg[:, 2] > 120) & (seg[:, 2] < 200)]
        rows.append(np.median(ok, axis=0) if len(ok) else np.array([0, 16, 172.0]))
    rows = np.array(rows); k = np.ones(5) / 5
    rows = np.stack([np.convolve(np.pad(rows[:, c], 2, mode="edge"), k, "valid") for c in range(3)], 1)
    return rows

def glyph_region(x0, y0, x1, y1, grow=3):
    """the 8's own pixels (white ink + its dark edge), grown by `grow` px, never past the gap before the %"""
    wm = whiteness(x0 - grow, y0 - grow, x1 + grow, y1 + grow) > 0.08
    wm[:, (x1 + 2) - (x0 - grow):] = False                     # stop at the gap before the %
    m = wm.copy()
    for _ in range(grow):
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]; m = g
    m[:, (x1 + 2) - (x0 - grow):] = False
    return m

out = A.copy(); name, path, w = best
EDGE = (0, 6, 110)                                   # the thin dark-navy edge round the badge's white type
for spot, (x0, y0, x1, y1) in SPOTS.items():
    px0, py0, px1, py1 = x0 - 3, y0 - 3, x1 + 3, y1 + 3
    m = glyph_region(x0, y0, x1, y1)
    navy = navy_fill(px0, py0, px1, py1)
    reg = out[py0:py1, px0:px1, :3]; reg[m] = np.broadcast_to(navy[:, None, :], reg.shape)[m]; out[py0:py1, px0:px1, :3] = reg
    # the 5: same height (figure height = the 8's ink height), same baseline, centred on the 8
    f = face(path, w, 400); l, t, r, b = f.getbbox("5"); l8, t8, r8, b8 = f.getbbox("8")
    scale = (y1 - y0) / (b8 - t8); size = 400 * scale
    fs = face(path, w, size * SS); l5, t5, r5, b5 = fs.getbbox("5"); l8s, t8s, r8s, b8s = fs.getbbox("8")
    cx = (x0 + x1) / 2 * SS; base = y1 * SS                # ink bottom of the 8 = baseline (+ overshoot) -> align ink bottoms
    W5, H5 = r5 - l5, b5 - t5; ox = cx - W5 / 2 - l5; oy = base - (b8s - b5) - b5
    Lw, Lh = (px1 - px0) * SS, (py1 - py0 + 4) * SS
    layer = Image.new("RGBA", (Lw, Lh), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.text((ox - px0 * SS, oy - py0 * SS), "5", font=fs, fill=(255, 255, 255, 255), stroke_width=int(1.2 * SS), stroke_fill=EDGE + (255,))
    layer = layer.resize((px1 - px0, py1 - py0 + 4), Image.LANCZOS)
    base_img = Image.fromarray(out[py0:py1 + 4, px0:px1].astype(np.uint8), "RGBA"); base_img.alpha_composite(layer)
    out[py0:py1 + 4, px0:px1] = np.asarray(base_img).astype(float)
    print(spot, "box", (x0, y0, x1, y1), "font", name, w, f"{size:.1f}px")
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").save(DST); print("wrote", DST)
