"""Build the NJ workout + detail IG reel segments.

usage: python3 build.py <work_dir>
  <work_dir>/all/   source clips from the Drive shoot (not committed)
  <work_dir>/seg/   output segments (00.mp4 ...), concatenated + mixed afterwards
Graphics come from gfx/ next to this file: cap/*.png (rendered by gfx/shoot_captions.js
from gfx/captions.html) and endcard.webp.
"""
import json, os, subprocess, sys

W = sys.argv[1]
A = os.path.join(W, "all") + "/"
O = os.path.join(W, "seg") + "/"
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gfx") + "/"
C = G + "cap/"
os.makedirs(O, exist_ok=True)

FIT = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30"
# iPhone clips are HLG / BT.2020 HDR. Tone-map to SDR BT.709 (mobius, 203-nit reference white),
# then pull saturation back slightly so they sit with the BT.709 DJI clips.
HLG = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,"
       "zscale=p=bt709,tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
       "eq=saturation=0.9:contrast=1.03")
SDR = "format=yuv420p"
TAG = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p", *TAG,
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100"]


def is_hlg(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=color_transfer", "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)["streams"][0].get("color_transfer") == "arib-std-b67"


# (source, in, duration, keep live audio, [(caption, t0, t1)])
SEGS = [
    ("IMG_4666.mov", 0.3, 1.5, False, [("c_hook", 0, 99)]),
    ("DJI_0049.mp4", 2.2, 1.2, False, [("c_come", 0, 99)]),
    "BOOK",
    ("IMG_4664.mov", 1.0, 1.3, False, [("c_keys", 0, 99)]),
    ("IMG_4673.mov", 1.0, 1.0, False, [("c_train", 0, 99)]),
    ("DJI_0062.mp4", 3.0, 1.2, False, [("c_lift", 0, 99)]),
    ("DJI_0057.mp4", 0.5, 0.9, False, [("c_detail", 0, 99)]),
    ("DJI_0064.mp4", 10.0, 1.1, False, []),
    ("DJI_0059.mp4", 5.0, 0.8, False, []),
    ("DJI_0065.mp4", 8.0, 1.0, False, []),
    ("IMG_4680.mov", 4.0, 0.8, False, []),
    ("DJI_0067.mp4", 2.0, 0.9, False, []),
    ("DJI_0058.mp4", 3.0, 0.7, False, []),
    ("IMG_4695.mov", 5.3, 2.4, True, [("c_chest", 0, 99)]),
    ("DJI_0075.mp4", 3.0, 0.9, False, []),
    ("DJI_0056.mp4", 8.0, 0.8, False, []),
    ("DJI_0070.mp4", 1.5, 1.4, False, [("c_walk", 0, 99)]),
    ("IMG_4693.mov", 4.6, 3.2, True, [("c_spot", 0, 1.0), ("c_quote", 1.0, 99)]),
    "END",
]


def run(cmd):
    subprocess.run(cmd, check=True)


def silence(d):
    return ["-f", "lavfi", "-t", str(d), "-i", "anullsrc=r=44100:cl=stereo"]


for i, s in enumerate(SEGS):
    out = O + f"{i:02d}.mp4"
    if s == "BOOK":
        # Real booking screen over the blurred walk-up shot; card pops in over 6 frames.
        d, src = 1.6, A + "IMG_4665.mov"
        fc = (f"[0:v]{HLG if is_hlg(src) else SDR},{FIT},gblur=sigma=28,eq=brightness=-0.10[bg];"
              "[2:v]format=rgba,scale=eval=frame:w='1080*(1+0.08*max(0\\,1-t/0.2))':"
              "h='1920*(1+0.08*max(0\\,1-t/0.2))'[ov];"
              "[bg][ov]overlay=x=(W-w)/2:y=(H-h)/2:eval=frame,format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", "-t", str(d), "-i", src, *silence(d),
             "-loop", "1", "-t", str(d), "-i", C + "book.png", "-filter_complex", fc,
             "-map", "[v]", "-map", "1:a", *ENC, "-t", str(d), out])
    elif s == "END":
        # Supplied end card (9:16): 6-frame scale pop, then a slow push-in.
        d = 4.8
        fc = ("[0:v]scale=1080:1920:flags=lanczos,format=rgba,fps=30,"
              "scale=eval=frame:w='trunc(1080*(1+0.06*max(0\\,1-t/0.2)+0.012*t)/2)*2':"
              "h='trunc(1920*(1+0.06*max(0\\,1-t/0.2)+0.012*t)/2)*2':flags=lanczos,"
              "crop=1080:1920,format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(d), "-i", G + "endcard.webp", *silence(d),
             "-filter_complex", fc, "-map", "[v]", "-map", "1:a", *ENC, "-t", str(d), out])
    else:
        src, ss, d, live, caps = s
        path = A + src
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(d), "-i", path]
        cmd += [] if live else silence(d)
        for name, _, _ in caps:
            cmd += ["-loop", "1", "-t", str(d), "-i", C + name + ".png"]
        first_cap = 1 if live else 2
        fc, last = f"[0:v:0]{HLG if is_hlg(path) else SDR},{FIT}[v0]", "v0"
        for k, (name, t0, t1) in enumerate(caps):
            fc += f";[{last}][{first_cap + k}:v]overlay=0:0:enable='between(t,{t0},{t1})'[v{k + 1}]"
            last = f"v{k + 1}"
        fc += f";[{last}]format=yuv420p[v]"
        amap = ["-map", "0:a:0", "-af", "aresample=44100,aformat=channel_layouts=stereo"] if live else ["-map", "1:a"]
        run(cmd + ["-filter_complex", fc, "-map", "[v]", *amap, *ENC, "-t", str(d), out])
    print("ok", i, s if isinstance(s, str) else s[0])
