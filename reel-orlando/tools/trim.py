#!/usr/bin/env python3
"""Footage for "The $99 QuickWash, Orlando": cut each shot's window from the client's proxies into assets/footage/.

Proxies (scratchpad hp/proxy = May driveway + July lot shoots; dirty/proxy = Jersey City rooftop shoot) are already 1080x1920
portrait, 30 fps, HLG HDR tone-mapped to SDR (zscale + hable, as reel-hp/tools/trim.py). One grade for every shoot, as reel-hp:
eq contrast 1.05, saturation 1.08. Each file starts at the shot's in point (media-start 0) with a 0.3 s tail handle; the clip's
own sound is kept (AAC). Nothing is scaled or cropped.

Plates: a readable plate is covered by a box blur that follows it. The tracker matches the plate patch frame to frame
(sum of squared differences on half-size grey frames, +-28 px search, template refreshed every frame) from an anchor box
read off one frame by eye, forwards and backwards. Static blur boxes cover a fixed area (a bucket's partial print).
Usage: python3 -I tools/trim.py <hp proxy dir> <dirty proxy dir> [shot ...]"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter
HP, DIRTY = sys.argv[1], sys.argv[2]; ONLY = set(sys.argv[3:])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "footage"); os.makedirs(OUT, exist_ok=True)
W, H, FPS, TAIL = 1080, 1920, 30, 0.3
G = "eq=contrast=1.05:saturation=1.08"
# name, proxy ("B/" = rooftop shoot), in (s), length (s, without the tail), track [(anchor_t, cx, cy, w, h)], static [(x, y, w, h)]
SHOTS = [
    ("s01-grille-van",    "IMG_6406",      7.9, 2.867, [(7.9, 320, 1224, 230, 170)], []),
    ("s02-van-kit",       "IMG_0012_1_18", 2.9, 1.633, [], []),
    ("s03-foam-hood",     "IMG_6394",      0.6, 1.633, [], []),
    ("s04-mitt-door",     "IMG_6405",      2.0, 1.633, [], []),
    ("s05-mitt-rocker",   "IMG_0012_1_22", 1.5, 1.633, [], []),
    ("s06-inside-door",   "B/IMG_2032",    0.0, 2.733, [], []),
    ("s07-mitt-window",   "IMG_6408",      4.3, 1.633, [], [(890, 1420, 190, 500)]),
    ("s08-wheel-brush",   "IMG_6382",      1.5, 1.633, [], []),
    ("s09-door-jamb",     "IMG_6402",     10.6, 1.633, [], []),
    ("s10-console-wipe",  "B/IMG_2034",   35.5, 1.633, [], []),
    ("s11-spray-wax",     "IMG_6392",      0.0, 2.2,   [], []),
    ("s12-clean-side",    "IMG_6438",      1.6, 1.633, [], []),
    ("s13-hero-front",    "IMG_6432",      2.0, 1.633, [], []),
    ("s14-rinse-roof",    "IMG_6400",      2.0, 2.567, [], []),
]

def track(frames, i0, cx, cy, w, h):
    """Centre of the box in every frame, matched from frame i0 outwards."""
    g = [np.asarray(Image.fromarray(f).convert("L").resize((W // 2, H // 2)), np.float32) for f in frames]
    pos = {i0: (cx, cy)}; R = 14; tw, th = w // 4, h // 4      # half-size frame, half-size template radius
    for step in (1, -1):
        x, y = cx // 2, cy // 2; i = i0
        while 0 <= i + step < len(frames):
            a, b = g[i], g[i + step]
            x0, y0 = max(tw, min(W // 2 - tw, x)), max(th, min(H // 2 - th, y))
            tpl = a[y0 - th:y0 + th, x0 - tw:x0 + tw]
            best = None
            for dy in range(-R, R + 1):
                for dx in range(-R, R + 1):
                    xx, yy = x0 + dx, y0 + dy
                    if xx - tw < 0 or yy - th < 0 or xx + tw > W // 2 or yy + th > H // 2: continue
                    s = float(((b[yy - th:yy + th, xx - tw:xx + tw] - tpl) ** 2).mean())
                    if best is None or s < best[0]: best = (s, xx, yy)
            x, y = x + best[1] - x0, y + best[2] - y0; i += step; pos[i] = (x * 2, y * 2)
    return [pos[i] for i in range(len(frames))]

def blur_box(img, x, y, w, h):
    x0, y0, x1, y1 = max(0, int(x)), max(0, int(y)), min(W, int(x + w)), min(H, int(y + h))
    if x1 - x0 < 4 or y1 - y0 < 4: return
    img.paste(img.crop((x0, y0, x1, y1)).filter(ImageFilter.BoxBlur(16)).filter(ImageFilter.BoxBlur(10)), (x0, y0))

for name, clip, a, dur, tracks, statics in SHOTS:
    if ONLY and name not in ONLY: continue
    src = os.path.join(DIRTY, clip[2:] + ".mp4") if clip.startswith("B/") else os.path.join(HP, clip + ".mp4")
    d = dur + TAIL; out = os.path.join(OUT, name + ".mp4")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", f"{d:.3f}", "-i", src, "-vf", f"{G},fps={FPS}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    frames = [f.copy() for f in np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)]
    boxes = [[] for _ in frames]
    for (t0, cx, cy, w, h) in tracks:
        cs = track(frames, min(len(frames) - 1, round((t0 - a) * FPS)), cx, cy, w, h)
        for i, (x, y) in enumerate(cs): boxes[i].append((x - w / 2, y - h / 2, w, h))
    for i in range(len(frames)): boxes[i] += statics
    if any(boxes):
        imgs = []
        for f, bs in zip(frames, boxes):
            im = Image.fromarray(f)
            for bx in bs: blur_box(im, *bx)
            imgs.append(np.asarray(im))
        frames = imgs
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-ss", str(a), "-t", f"{d:.3f}", "-i", src, "-map", "0:v", "-map", "1:a?", "-shortest",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in frames: enc.stdin.write(np.ascontiguousarray(f).tobytes())
    enc.stdin.close(); enc.wait()
    print(f"{name:20s} {clip:14s} {a:5.2f}+{dur:.3f}  frames {len(frames)}  blur boxes {sum(len(b) for b in boxes)}")
