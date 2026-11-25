#!/usr/bin/env python3
"""Trim the Orlando shots from the client's proxies into assets/footage/ (reel-hp's grade: eq contrast 1.05, saturation 1.08;
H.264 CRF 18 yuv420p 30 fps, AAC kept). Each file starts at the shot's in point (media-start 0) and carries a 0.3 s tail
handle. The one readable plate in a window (X39-RVK on IMG_0012_1_13) gets reel-hp's tracked box blur (same keyframes).

Usage: python3 -I tools/trim.py <hp proxy dir> <dirty-shoot proxy dir> [name ...]"""
import os, subprocess, sys
HP, DIRTY = sys.argv[1], sys.argv[2]; ONLY = set(sys.argv[3:])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "footage"); os.makedirs(OUT, exist_ok=True)
G = "eq=contrast=1.05:saturation=1.08"
# name, proxy ("B/" = dirty shoot), in, length, plate track [(src_t, cx, cy)], box w, h
SHOTS = [
    ("h-crumb-carpet", "B/IMG_2034", 1.0, 4.1, None, 0, 0),         # hook: crumbs and grit on the passenger carpet, steady slow push
    ("o-van-logo", "B/IMG_3730", 0.0, 1.45, None, 0, 0),            # offer: dolly past the QuickWash van, logo filling the frame
    ("o-detailer-driveway", "IMG_0012_1_13", 1.3, 2.55,             # offer: detailer (QuickWash hoodie) at the SUV in a house driveway
     [(1.0, 1095, 1144), (1.4, 1075, 1143), (1.8, 1040, 1145), (2.2, 1024, 1155),
      (2.6, 986, 1168), (3.0, 955, 1175), (3.4, 924, 1178), (3.8, 901, 1183), (4.2, 880, 1186)], 170, 130),
    ("l-foam-street", "IMG_0012_1_14", 4.5, 1.7, None, 0, 0),       # list: wide street, detailer foam-cannons the SUV white
    ("l-open-door", "IMG_6439", 0.1, 2.1, None, 0, 0),              # list: driver door open on the clean interior
    ("l-wheel-rinse", "IMG_0012_1_5", 0.6, 3.05, None, 0, 0),       # list: detailer crouched rinsing the rear wheel and tire, houses behind
    ("p-hero-front", "IMG_6432", 2.0, 3.7, None, 0, 0),             # price: finished black car, slow arc on the front
    ("u-detailer-house", "IMG_0012_1_16", 1.4, 3.0, None, 0, 0),    # urgency: detailer foaming the car by a house and picket fence
]

def lerp(keys, t0, off, lo, hi):
    pts = [(k[0] - t0, k[1] - off) for k in keys]; e = str(pts[-1][1])
    for (ta, va), (tb, vb) in reversed(list(zip(pts, pts[1:]))):
        e = f"if(lt(t,{tb:.3f}),{va}+({vb}-{va})*(t-{ta:.3f})/{tb - ta:.3f},{e})"
    return f"max({lo},min({hi},if(lt(t,{pts[0][0]:.3f}),{pts[0][1]},{e})))"

for name, clip, a, dur, track, bw, bh in SHOTS:
    if ONLY and name not in ONLY: continue
    src = os.path.join(DIRTY, clip[2:] + ".mp4") if clip.startswith("B/") else os.path.join(HP, clip + ".mp4")
    d = dur + 0.3
    if track:
        x = lerp(track, a, bw // 2, 0, 1080 - bw); y = lerp(track, a, bh // 2, 0, 1920 - bh)
        fc = (f"[0:v]{G},split[a][b];[b]crop={bw}:{bh}:'{x}':'{y}',boxblur=20:4[bl];"
              f"[a][bl]overlay='{x}':'{y}',fps=30,format=yuv420p[v]")
    else:
        fc = f"[0:v]{G},fps=30,format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a), "-t", f"{d:.3f}", "-i", src, "-filter_complex", fc,
                    "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", os.path.join(OUT, name + ".mp4")], check=True)
    print(name, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(OUT, name + ".mp4")],
                                capture_output=True, text=True).stdout.strip())
