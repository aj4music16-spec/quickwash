#!/usr/bin/env python3
"""Orlando end card (from reel-odessa/tools/endcard_pill.py): repaint the location pill on assets/app/endcard.jpg.

1. Erase the old pill (x 222-858, y 248-344) by rebuilding the blue background column by column: each column is a
   linear blend between the clean rows just above (y 243-246) and below (y 348-351) the pill, so the card's own
   centre-dark vignette carries through with no patch edge.
2. Draw a new pill in the same style: 7 px cyan outline (sampled #02E6FD on the Davenport card), fully rounded, 80 px tall, centred on
   x 540, y 256-335, with 65 px side padding (PAD); white uppercase Montserrat ExtraBold (800) at the original cap height.
Usage: python3 tools/endcard_pill.py <font.ttf> <text> <in.jpg> <out.jpg>
"""
import sys
from PIL import Image, ImageDraw, ImageFont

font_path, text, src, out = sys.argv[1:5]
PAD = 65                                 # side padding to the text, as on the supplied Davenport card (text 299-785 in outline 234-845)
SS = 4                                   # supersample for smooth edges
im = Image.open(src).convert("RGB")
px = im.load()
X0, X1, Y0, Y1 = 222, 858, 248, 344      # erase box (covers the old pill plus its anti-aliased edge)
A0, A1, B0, B1 = 243, 247, 348, 352      # clean rows above / below
for x in range(X0, X1 + 1):
    top = [sum(px[x, y][c] for y in range(A0, A1)) / (A1 - A0) for c in range(3)]
    bot = [sum(px[x, y][c] for y in range(B0, B1)) / (B1 - B0) for c in range(3)]
    for y in range(Y0, Y1 + 1):
        k = (y - (A0 + A1) / 2) / ((B0 + B1) / 2 - (A0 + A1) / 2)
        px[x, y] = tuple(round(top[c] + (bot[c] - top[c]) * k) for c in range(3))

font = ImageFont.truetype(font_path, 38.6 * SS)   # Montserrat ExtraBold 38.6 px = the original 520 x 28 px caps
bb = font.getbbox(text)
tw, th = (bb[2] - bb[0]) / SS, (bb[3] - bb[1]) / SS
pad, top_y, h, stroke = PAD, 256, 80, 7
w = tw + 2 * pad
left = 540 - w / 2
ov = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
d.rounded_rectangle([left * SS, top_y * SS, (left + w) * SS - 1, (top_y + h) * SS - 1], radius=h * SS // 2,
                    outline=(2, 230, 253, 255), width=stroke * SS)
cap_top = 281                            # the original's cap top (caps 281-309)
d.text((540 * SS - (bb[0] + bb[2]) / 2, cap_top * SS - bb[1]), text, font=font, fill=(255, 255, 255, 255))
ov = ov.resize(im.size, Image.LANCZOS)
im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
im.save(out, quality=95, subsampling=0)
print(f"pill x {left:.0f}-{left + w:.0f}, y {top_y}-{top_y + h}; text {tw:.0f} x {th:.0f}")
