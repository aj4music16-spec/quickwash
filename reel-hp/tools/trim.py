#!/usr/bin/env python3
"""Trims the chosen proxies into assets/footage/ for "The $99 Tag".

Each file = the shot window plus 0.5 s handles (clamped at the clip start), re-encoded H.264
crf 18 yuv420p faststart with its audio. A mild, uniform grade (eq contrast 1.05, saturation 1.08)
is applied in this step, never as a CSS filter. Readable plates are blurred with a tracked box:
the plate centre was read off gridded frames every 0.3-0.4 s and is interpolated linearly.

Usage: python3 tools/trim.py <proxy_dir>
"""
import os, subprocess, sys

PROXY = sys.argv[1] if len(sys.argv) > 1 else "proxy"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "footage")
GRADE = "eq=contrast=1.05:saturation=1.08"

# name, source clip, shot in, shot out, plate track [(src_t, cx, cy)], box w, box h
SHOTS = [
    ("s01-foam-sheet",        "IMG_0012",      10.2, 12.0, None, 0, 0),
    ("s02-detailer-driveway", "IMG_0012_1_13",  1.5,  3.3,
     [(1.0, 1095, 1144), (1.4, 1075, 1143), (1.8, 1040, 1145), (2.2, 1024, 1155),
      (2.6, 986, 1168), (3.0, 955, 1175), (3.4, 924, 1178), (3.8, 901, 1183)], 170, 130),
    ("s03-mitt-bumper",       "IMG_0012_1_21",  1.3,  2.5, None, 0, 0),
    ("s04-clean-footwell",    "IMG_6436",       1.4,  2.6, None, 0, 0),
    ("s05-windshield-rinse",  "IMG_6397",       4.4,  5.6,
     [(3.9, 255, 1322), (4.2, 252, 1307), (4.5, 252, 1287), (4.8, 248, 1280), (5.1, 248, 1270),
      (5.4, 240, 1257), (5.7, 222, 1230), (6.1, 192, 1202)], 270, 180),
    ("s06-wheel-rinse",       "IMG_6386",       4.8,  6.0, None, 0, 0),
    ("s07-clean-dash",        "IMG_6439",       1.8,  3.0, None, 0, 0),
    ("s08-spray-hood",        "IMG_6393",       0.3,  1.5,
     [(0.0, 207, 1275), (0.3, 247, 1285), (0.6, 277, 1300), (0.9, 290, 1317), (1.2, 282, 1340),
      (1.5, 255, 1360), (1.8, 227, 1380), (2.1, 195, 1390)], 370, 220),
    ("s09-hero-front",        "IMG_6432",       2.5,  4.9, None, 0, 0),
    ("s10-detailer-house",    "IMG_0012_1_12",  0.3,  2.1,
     [(0.0, 540, 1100), (0.35, 488, 1100), (0.7, 495, 1085), (1.05, 485, 1150), (1.4, 435, 1160),
      (1.75, 452, 1162), (2.1, 450, 1155), (2.6, 455, 1120)], 170, 140),
    ("s11-detailer-logo",     "IMG_0012_1_15",  0.3,  2.5, None, 0, 0),
]


def lerp_expr(keys, t0, off, lo, hi):
    """Piecewise-linear ffmpeg expression in trimmed time t, minus `off`, clamped to [lo, hi]."""
    pts = [(k[0] - t0, k[1] - off) for k in keys]
    expr = str(pts[-1][1])
    for (ta, va), (tb, vb) in reversed(list(zip(pts, pts[1:]))):
        expr = f"if(lt(t,{tb:.3f}),{va}+({vb}-{va})*(t-{ta:.3f})/{tb - ta:.3f},{expr})"
    expr = f"if(lt(t,{pts[0][0]:.3f}),{pts[0][1]},{expr})"
    return f"max({lo},min({hi},{expr}))"


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, clip, a, b, track, bw, bh in SHOTS:
        s, e = max(0.0, a - 0.5), b + 0.5
        src = os.path.join(PROXY, clip + ".mp4")
        v = f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,{GRADE}"
        if track:
            xs = [(k[0], k[1]) for k in track]
            ys = [(k[0], k[2]) for k in track]
            X = lerp_expr(xs, s, bw // 2, 0, 1080 - bw)
            Y = lerp_expr(ys, s, bh // 2, 0, 1920 - bh)
            v += (f",split[base][c];[c]crop=w={bw}:h={bh}:x='{X}':y='{Y}',boxblur=lr=28:lp=4[b];"
                  f"[base][b]overlay=x='{X}':y='{Y}'[v]")
        else:
            v += "[v]"
        fc = v + f";[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a]"
        out = os.path.join(OUT, name + ".mp4")
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-filter_complex", fc,
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", out]
        subprocess.run(cmd, check=True)
        print(f"{name:24s} {clip:15s} src {s:.2f}-{e:.2f}  shot {a:.2f}-{b:.2f}  media-start {a - s:.2f}"
              + ("  plate blurred" if track else ""))


if __name__ == "__main__":
    main()
