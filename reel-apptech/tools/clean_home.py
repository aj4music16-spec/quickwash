"""Privacy patch for the client's home screenshot: replace the greeting name and the street address.
Usage: python3 -I tools/clean_home.py assets/app/screen-home.png assets/app/screen-home-clean.png
For each text line: find its ink bbox, fit Inter (weight + size) to the original line by rendering the original string and
minimising the pixel error, paint the bbox over with the flat background colour, then set the replacement string with the
fitted font at the same left edge and baseline, in the measured ink colour."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, DST = sys.argv[1], sys.argv[2]
FONTS = {w: f"/usr/share/fonts/opentype/inter/Inter-{w}.otf" for w in ["Light", "Regular", "Medium", "SemiBold", "Bold"]}
im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(int)

# (region to search, original text, replacement, background rgb)
JOBS = [
    ((200, 200, 560, 275), "Hi AJ Oteyza!", "Hi Alex!", (255, 102, 0)),
    ((170, 1370, 1060, 1430), "45 Brookwood St, East Orange, NJ 07018", "123 Main St, Your City", (255, 255, 255)),
]

def ink_mask(reg, bg):
    return np.abs(reg - np.array(bg)).sum(axis=2) > 60

def render(text, font, size, bg, fg):
    img = Image.new("RGB", size, bg); ImageDraw.Draw(img).text((0, 0), text, font=font, fill=fg)
    return img

for (x0, y0, x1, y1), old, new, bg in JOBS:
    reg = a[y0:y1, x0:x1]
    m = ink_mask(reg, bg)
    ys, xs = np.where(m)
    bx0, by0, bx1, by1 = x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1
    # ink colour: the pixel furthest from the background
    d = np.abs(reg - np.array(bg)).sum(axis=2)
    fy, fx = np.unravel_index(d.argmax(), d.shape)
    fg = tuple(int(v) for v in reg[fy, fx])
    W, H = bx1 - bx0, by1 - by0
    orig = a[by0:by1, bx0:bx1]
    best = None
    for w, path in FONTS.items():
        for s10 in range(300, 700, 2):
            s = s10 / 10
            f = ImageFont.truetype(path, s)
            l, t, r, b = f.getbbox(old)
            if abs((r - l) - W) > 6: continue
            img = Image.new("RGB", (W + 40, H + 40), bg)
            ImageDraw.Draw(img).text((-l, -t), old, font=f, fill=fg)
            cand = np.asarray(img).astype(int)[:H, :W]
            err = np.abs(cand - orig).mean()
            if best is None or err < best[0]: best = (err, w, s, l, t)
    err, w, s, l, t = best
    f = ImageFont.truetype(FONTS[w], s)
    print(f"{old!r}: bbox {bx0},{by0}-{bx1},{by1}  ink {fg}  fit Inter {w} {s}px  err {err:.2f}")
    draw = ImageDraw.Draw(im)
    draw.rectangle((bx0 - 6, by0 - 6, bx1 + 6, by1 + 6), fill=bg)
    # same origin as the fitted original: left ink edge and top-of-ink anchored through the font's own bbox offsets
    draw.text((bx0 - l, by0 - t), new, font=f, fill=fg)

im.save(DST)
print("wrote", DST)
