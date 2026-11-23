"""The Clean-Car Effect — director's cut. Cartoon stills as chapter cards, real footage as proof, fast cuts.

usage: python3 directors_cut.py <footage_dir> <gym_dir> <work_dir> <out.mp4>
  <footage_dir>  night-batch footage (tim/, jc/, cs/index.txt)      <gym_dir>  gym shoot clips (IMG_4693.mov ...)
Reuses the cutting helpers in ../reels-night/build.py. Voice and effect cues are markers inside SHOTS,
so their timing follows the cut when shots are added, removed or re-timed.
"""
import math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOOT, GYM, WORK, OUT = sys.argv[1:5]
sys.argv = [sys.argv[0], FOOT, WORK]
sys.path.insert(0, os.path.join(HERE, "../reels-night"))
import build as b                                              # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont      # noqa: E402

os.makedirs(WORK, exist_ok=True)
SRC = os.path.join(HERE, "assets/src")
A = os.path.join(HERE, "assets/audio")
SFX = os.path.join(HERE, "../reel-detaileros/assets/audio")
FRED = os.path.join(HERE, "assets/fonts/fredoka-latin-700-normal.woff")
CREAM, DEEP, ORANGE = (255, 244, 220), (58, 22, 104), (255, 122, 20)
W, H = 1080, 1920
T, J = b.T, b.J
G = lambda n: os.path.join(GYM, n)
S = lambda n: os.path.join(SRC, n + ".png")


# ---------- graphics ----------
def fit_font(lines, size, max_w=960):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    while size > 40:
        f = ImageFont.truetype(FRED, size)
        if max(d.textlength(ln, font=f) for ln in lines) <= max_w:
            return f, size
        size -= 4
    return f, size


def text_layer(lines, size, fill=CREAM, max_w=960):
    """Chunky cream caps with a deep-purple outline and soft shadow, to match the cartoon lettering."""
    f, size = fit_font(lines, size, max_w); lh = int(size * 1.08); pad = 40
    d0 = ImageDraw.Draw(Image.new("RGB", (8, 8))); w = int(max(d0.textlength(ln, font=f) for ln in lines)) + pad * 2
    img = Image.new("RGBA", (w, lh * len(lines) + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); dm = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = (w - d0.textlength(ln, font=f)) / 2; y = pad + i * lh - size * 0.12
        ds.text((x, y + 12), ln, font=f, fill=(20, 6, 40, 190), stroke_width=10, stroke_fill=(20, 6, 40, 190))
    img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), img); dm = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = (w - d0.textlength(ln, font=f)) / 2; y = pad + i * lh - size * 0.12
        dm.text((x, y), ln, font=f, fill=fill + (255,), stroke_width=9, stroke_fill=DEEP + (255,))
    return img


def cap_png(path, text, size=108, y=1120):
    lay = text_layer(text.upper().split("\n"), size); img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(lay, ((W - lay.width) // 2, y), lay); img.save(path)


# ---------- segment builders ----------
def seg_clip(out, src, ss, d, cap=None, zoom=1.0, ax=0.5, ay=0.5):
    """Footage shot. zoom/ax/ay crop in on a region (used to keep a licence plate out of frame)."""
    zw, zh = int(W * zoom / 2) * 2, int(H * zoom / 2) * 2
    vf = ((b.HLG if b.is_hlg(src) else "format=yuv420p") + f",scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={zw}:{zh},crop={W}:{H}:{int((zw-W)*ax)}:{int((zh-H)*ay)},fps=30")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(d + 0.2), "-i", src]; fc = f"[0:v:0]{vf}[v0]"; last = "v0"
    if cap:
        cmd += ["-loop", "1", "-t", str(d), "-i", cap]; fc += ";[v0][1:v]overlay=0:0[v1]"; last = "v1"
    b.run(cmd + ["-filter_complex", fc + f";[{last}]format=yuv420p[v]", "-map", "[v]", *b.ENC, "-t", str(d), out])


def seg_still(out, img, d, punch=True):
    """Cartoon card: hard punch-in over 4 frames, then a slow drift. The opening card skips the punch."""
    z = "(1+0.14*max(0\\,1-t/0.13)+0.03*t)" if punch else "(1+0.035*t)"
    fc = (f"[0:v]scale={W}:{H}:flags=lanczos,fps=30,scale=eval=frame:w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':flags=lanczos,"
          f"crop={W}:{H},format=yuv420p[v]")
    b.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(d), "-i", img, "-filter_complex", fc, "-map", "[v]", *b.ENC, "-t", str(d), out])


def seg_card(out, d, card):
    """Booking card in the cartoon's purple world: headline slams in, card pops, 'Book This Slot' gets tapped."""
    fd = out + "_frames"; os.makedirs(fd, exist_ok=True)
    bg = Image.new("RGB", (W, H)); px = bg.load()
    for y in range(H):
        k = y / H; col = (int(112 + 44 * k), int(40 + 46 * k), int(176 + 40 * k))
        for x in range(W):
            px[x, y] = col
    h1 = text_layer(["BOOK IN"], 130); h2 = text_layer(["20 SECONDS."], 150, fill=(255, 196, 92))
    c = Image.open(card).convert("RGBA"); c = c.resize((620, int(620 * c.height / c.width)), Image.LANCZOS)
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 46, fill=255); c.putalpha(m)
    pad = 90; cl = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", cl.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 26, pad + c.width, pad + c.height + 26), 46, fill=(30, 8, 60, 150))
    cl = Image.alpha_composite(cl, sh.filter(ImageFilter.GaussianBlur(30))); cl.paste(c, (pad, pad), c)
    back = lambda p, s=1.8: 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2
    pr = lambda t, t0, dd: min(1, max(0, (t - t0) / dd))

    def put(frame, layer, cx, cy, scale, alpha=1.0):
        if alpha <= 0:
            return
        l = layer.resize((max(2, int(layer.width * scale)), max(2, int(layer.height * scale))), Image.BILINEAR)
        if alpha < 1:
            l.putalpha(l.getchannel("A").point(lambda a: int(a * alpha)))
        frame.paste(l, (int(cx - l.width / 2), int(cy - l.height / 2)), l)

    TAP = 1.05
    for n in range(int(d * 30)):
        t = n / 30; fr = bg.copy().convert("RGBA")
        a = pr(t, 0.0, 0.3); put(fr, h1, W / 2, 300 - 60 * (1 - a) ** 3, 0.85 + 0.15 * back(a), min(1, a * 3))
        s2 = pr(t, 0.2, 0.34); put(fr, h2, W / 2, 475, 1.55 - 0.55 * back(s2, 2.2) if s2 < 1 else 1.0, min(1, s2 * 3))
        cp = pr(t, 0.12, 0.42); press = math.sin(math.pi * pr(t, TAP, 0.2)) * 0.02
        cy = 1110 + 140 * (1 - cp) ** 3 + math.sin(max(0, t - 0.6) * 2.4) * 6
        put(fr, cl, W / 2, cy, (0.7 + 0.3 * back(cp, 1.5)) - press, min(1, cp * 3))
        r = pr(t, TAP, 0.45)
        if 0 < r < 1:
            rad = 30 + 130 * (1 - (1 - r) ** 3); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); by = cy + c.height / 2 - 56
            ImageDraw.Draw(ov).ellipse((W / 2 - rad, by - rad, W / 2 + rad, by + rad), fill=(255, 255, 255, int(70 * (1 - r))), outline=(255, 255, 255, int(235 * (1 - r))), width=7)
            fr = Image.alpha_composite(fr, ov)
        fr.convert("RGB").save(os.path.join(fd, f"f{n:04d}.jpg"), quality=93)
    b.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(fd, "f%04d.jpg"), *b.ENC, "-t", str(d), out])


# ---------- the cut ----------
C = lambda text: dict(text=text)
SHOTS = [
    # hook — "Your car isn't dirty. It's carrying your whole week."
    ("vo", "v1", 0.1),
    ("still", S("mess"), 0.7, False), ("still", S("mind"), 0.6),
    ("clip", T(52), 3.0, 0.5, C("Your whole week")), ("clip", T(63), 0.3, 0.45, C("Your whole week")), ("clip", J(41), 3.6, 0.45, C("Your whole week")),
    # the turn
    ("sfx", "whoosh", -0.05, 0.5), ("vo", "v2", 0.05),
    ("clip", T(58), 1.0, 0.65, C("Don't drive to\na car wash")), ("clip", T(61), 2.4, 0.65, C("Don't drive to\na car wash")),
    # book
    ("vo", "v3", 0.05), ("sfx", "pop", 0.14, 0.5), ("sfx", "tap", 1.05, 1.4),
    ("card", 1.8, os.path.join(HERE, "../reel-nj-gym/gfx/book_crop.png")),
    # arrival — "We pull up with the water, the power, and the pros."
    ("vo", "v4", 0.05), ("sfx", "whoosh", -0.05, 0.55), ("sfx", "splash", 0.0, 0.4),
    ("still", S("reset"), 0.55),
    ("clip", T(42), 3.4, 0.75, C("The water.")), ("clip", J(45), 0.8, 0.7, C("The power.")), ("clip", T(44), 0.6, 0.8, C("The pros.")),
    # rapid montage — one word per beat
    ("vo", "v5", 0.05),
    ("clip", T(22), 3.2, 0.35, C("Foam.")), ("clip", J(20), 2.6, 0.3, C("Foam.")),
    ("clip", T(16), 0.9, 0.3, C("Wheels.")), ("clip", T(84), 6.2, 0.25, C("Wheels.")),
    ("clip", T(98), 2.2, 0.4, C("Vacuum.")), ("clip", T(93), 1.2, 0.35, C("Vacuum.")),
    ("clip", T(96), 3.2, 0.35, C("Every seat.")), ("clip", T(28), 2.0, 0.3, C("Every seat.")),
    ("clip", T(94), 3.6, 0.45, C("Every cup holder.")), ("clip", T(111), 1.4, 0.45, C("Every cup holder.")),
    # payoff
    ("vo", "v6", 0.1),
    ("clip", T(106), 0.6, 0.45, None), ("clip", T(101), 1.2, 0.4, None),
    ("sfx", "sparkle", 0.0, 0.45), ("still", S("effect"), 0.65),
    # a real customer's reaction, live audio (cropped in to keep the licence plate out of frame)
    ("live", G("IMG_4693.mov"), 5.45, 2.15, C("“Wow. It’s so good.”"), dict(zoom=1.2, ax=1.0, ay=0.0)),
    # proof — "Over ten thousand services. Two hundred five-star reviews."
    ("vo", "v8", 0.05),
    ("clip", T(104), 2.2, 0.85, C("10,000+ services")), ("clip", T(103), 0.6, 0.85, C("10,000+ services")),
    ("clip", J(38), 2.2, 0.7, C("200+ five-star\nreviews")), ("clip", G("IMG_4694.mov"), 0.8, 0.95, C("200+ five-star\nreviews")),
    # close
    ("vo", "v9", 0.1), ("sfx", "whoosh", -0.05, 0.55),
    ("still", S("fresh"), 0.8),
    ("sfx", "pop", 0.0, 0.45), ("end", 2.3),
]

files, t, vo, sfx, live = [], 0.0, [], [], None
caps = {}
for i, s in enumerate(SHOTS):
    kind = s[0]
    if kind == "vo":
        vo.append((s[1], t + s[2])); continue
    if kind == "sfx":
        sfx.append((s[1], max(0, t + s[2]), s[3])); continue
    out = os.path.join(WORK, f"{i:02d}.mp4")
    if kind == "still":
        d = s[2]; seg_still(out, s[1], d, punch=(len(s) < 4 or s[3]))
    elif kind in ("clip", "live"):
        src, ss, d, cap = s[1:5]; png = None
        if cap:
            key = cap["text"]
            if key not in caps:
                caps[key] = os.path.join(WORK, f"cap{len(caps):02d}.png"); cap_png(caps[key], **cap)
            png = caps[key]
        seg_clip(out, src, ss, d, png, **(s[5] if len(s) > 5 else {}))
        if kind == "live":
            live = (src, ss, d, t)
    elif kind == "card":
        d = s[1]; seg_card(out, d, s[2])
    elif kind == "end":
        d = s[1]; b.seg_qw_end(out, d)
    t += d; files.append(out)
dur = t
lst = os.path.join(WORK, "list.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
video = os.path.join(WORK, "video.mp4"); b.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
print(f"cut {len(files)} shots, {dur:.2f}s; vo {[(n, round(x, 2)) for n, x in vo]}; live at {live[3]:.2f}")

# ---------- audio: music ducks under voice and effects ----------
lms = int(live[3] * 1000)
args = ["-i", video, "-i", os.path.join(A, "music2.mp3"), "-ss", str(live[1]), "-t", str(live[2]), "-i", live[0]]
fc = (f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.05,afade=t=out:st={dur-0.9}:d=0.9,apad=whole_dur={dur}[bed];"
      f"[2:a]aresample=44100,aformat=channel_layouts=stereo,highpass=f=90,volume=2.4,afade=t=in:d=0.05,afade=t=out:st={live[2]-0.08}:d=0.08,adelay={lms}|{lms}[live];")
i, lab = 3, ""
for name, at, g in sfx:
    p = os.path.join(A, name + ".wav"); p = p if os.path.exists(p) else os.path.join(SFX, name + ".wav")
    args += ["-i", p]; ms = int(at * 1000); fc += f"[{i}:a]aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[s{i}];"; lab += f"[s{i}]"; i += 1
fc += f"{lab}amix=inputs={len(sfx)}:normalize=0:duration=longest,apad=whole_dur={dur},volume=1.3,asplit[sfx][sc];"
vl = "[live]"
for name, at in vo:
    args += ["-i", os.path.join(A, "vo2", name + ".wav")]; ms = int(at * 1000)
    fc += f"[{i}:a]aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}];"; vl += f"[v{i}]"; i += 1
fc += (f"{vl}amix=inputs={len(vo)+1}:normalize=0:duration=longest,apad=whole_dur={dur},highpass=f=80,"
       "acompressor=threshold=0.1:ratio=3:attack=5:release=120,volume=2.2,asplit[vo][vsc];"
       "[bed][sc]sidechaincompress=threshold=0.03:ratio=5:attack=4:release=220[b1];"
       "[b1][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=250[b2];"
       "[b2][sfx][vo]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.7,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", OUT], check=True)
print("mixed", OUT)
