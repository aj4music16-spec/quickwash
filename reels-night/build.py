"""Night batch: four reels cut from Drive footage (QuickWash x2, DetailerOS x2).

usage: python3 build.py <footage_dir> <work_dir> [reel ...]
  <footage_dir>/tim/  Tim's 5/1 Content Day clips      (index in cs/index.txt)
  <footage_dir>/jc/   Jersey City Durango clips
  <footage_dir>/dos/  DetailerOS screen recordings (storefront.mp4, booking.mp4)
Outputs <work_dir>/<reel>/video.mp4 (silent); mix.py adds voice, music and effects.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FOOT, WORK = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]
W, H = 1080, 1920
NAVY, ORANGE, GREEN = (1, 0, 154), (255, 101, 1), (31, 160, 84)
F700 = os.path.join(HERE, "fonts/poppins-latin-700-normal.woff")
F600 = os.path.join(HERE, "fonts/poppins-latin-600-normal.woff")
QW_END = os.path.join(HERE, "../reel-nj-gym/gfx/endcard.webp")
DOS_REEL = os.path.join(HERE, "../dist/detaileros-quote-to-paid.mp4")   # its last 3.45 s is the DetailerOS end card

FIT = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30"
HLG = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,"
       "zscale=p=bt709,tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=saturation=0.9:contrast=1.03")
ENC = ["-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]

INDEX = {}
for line in open(os.path.join(FOOT, "cs/index.txt")):
    g, i, name, _ = line.split()
    INDEX[(g, int(i))] = os.path.join(FOOT, g, name + ".mp4")


def run(cmd):
    subprocess.run(cmd, check=True)


def is_hlg(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)["streams"][0].get("color_transfer") == "arib-std-b67"


# ---------- graphics ----------
def font(size, bold=True):
    return ImageFont.truetype(F700 if bold else F600, size)


def shadowed(draw_fn):
    """Draw white text with a soft dark shadow so it reads on any footage."""
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(sh), (0, 0, 0, 215))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    sh2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(sh2), (0, 0, 0, 200))
    sh = Image.alpha_composite(sh, sh2.filter(ImageFilter.GaussianBlur(2)))
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(top), (255, 255, 255, 255))
    return Image.alpha_composite(sh, top)


def cap_png(path, text=None, pill=None, check=False, y=1190, size=68):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if text:
        f = font(size); lines = text.split("\n")
        def draw(d, col):
            for i, ln in enumerate(lines):
                w = d.textlength(ln, font=f); x = (W - w) / 2 + (44 if check and i == 0 else 0)
                d.text((x, y + i * size * 1.2), ln, font=f, fill=col)
        img = Image.alpha_composite(img, shadowed(draw))
        if check:
            d = ImageDraw.Draw(img); w = d.textlength(lines[0], font=f); cx = (W - w) / 2 - 44 + 0; cy = y + size * 0.72; r = 34
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN + (255,))
            d.line((cx - 15, cy + 1, cx - 4, cy + 12, cx + 16, cy - 11), fill=(255, 255, 255, 255), width=8, joint="curve")
    if pill:
        f = font(50); d = ImageDraw.Draw(img); py = 250
        for i, ln in enumerate(pill.split("\n")):
            w = d.textlength(ln, font=f); x0 = (W - w) / 2 - 28; yy = py + i * 84
            d.rounded_rectangle((x0, yy, x0 + w + 56, yy + 74), 18, fill=(255, 255, 255, 255))
            d.text((x0 + 28, yy + 2), ln, font=f, fill=(17, 17, 17, 255))
    img.save(path)


PH_W, PH_H, PH_X, PH_Y = 664, 1444, 208, 400      # phone screen box on the 1080x1920 stage


def phone_bg(path, head, head2=None):
    """Light brand background with a phone body; headline in navy, optional second line in orange."""
    img = Image.new("RGBA", (W, H), (245, 247, 252, 255)); d = ImageDraw.Draw(img)
    f = font(84); yy = 110
    for ln, col in ((head, (13, 20, 64)), (head2, ORANGE)):
        if ln:
            w = d.textlength(ln, font=f); d.text(((W - w) / 2, yy), ln, font=f, fill=col + (255,)); yy += 104
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((PH_X - 22, PH_Y + 10, PH_X + PH_W + 22, PH_Y + PH_H + 60), 96, fill=(10, 20, 60, 90))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(34))); d = ImageDraw.Draw(img)
    d.rounded_rectangle((PH_X - 20, PH_Y - 20, PH_X + PH_W + 20, PH_Y + PH_H + 20), 92, fill=(22, 24, 30, 255))
    img.convert("RGB").save(path)


def phone_mask(path):
    m = Image.new("L", (PH_W * 2, PH_H * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, PH_W * 2 - 1, PH_H * 2 - 1), 144, fill=255)
    m.resize((PH_W, PH_H), Image.LANCZOS).save(path)


def dm_frames(outdir, dur, bubbles, head):
    """Stack of incoming DM bubbles popping in over a dark chat background."""
    os.makedirs(outdir, exist_ok=True); f = font(54, False); fh = font(76)
    for n in range(int(dur * 30)):
        t = n / 30; img = Image.new("RGB", (W, H), (14, 16, 26)); d = ImageDraw.Draw(img)
        w = d.textlength(head, font=fh); d.text(((W - w) / 2, 250), head, font=fh, fill=(255, 255, 255))
        y = 520
        for (t0, text) in bubbles:
            if t >= t0:
                p = min(1, (t - t0) / 0.22); e = 1 - (1 - p) ** 3; s = 0.7 + 0.3 * e + 0.06 * (1 - abs(2 * p - 1)) * (p < 1)
                tw = d.textlength(text, font=f); bw, bh = tw + 80, 118
                layer = Image.new("RGBA", (int(bw) + 8, bh + 8), (0, 0, 0, 0))
                ld = ImageDraw.Draw(layer); ld.rounded_rectangle((0, 0, bw, bh), 56, fill=(46, 50, 68, 255)); ld.text((40, 22), text, font=f, fill=(255, 255, 255, 255))
                layer = layer.resize((max(2, int(layer.width * s)), max(2, int(layer.height * s))), Image.LANCZOS)
                layer.putalpha(layer.getchannel("A").point(lambda a: int(a * e)))
                img.paste(layer, (70, int(y + (bh - layer.height) / 2)), layer)
            y += 150
        img.save(os.path.join(outdir, f"f{n:04d}.jpg"), quality=92)


# ---------- segment builders ----------
def seg_clip(out, src, ss, d, cap, speed=1.0):
    vf = (HLG if is_hlg(src) else "format=yuv420p") + "," + (f"setpts={1/speed}*PTS," if speed != 1 else "") + FIT
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(d * speed + 0.2), "-i", src]
    fc = f"[0:v:0]{vf}[v0]"; last = "v0"
    if cap:
        cmd += ["-loop", "1", "-t", str(d), "-i", cap]; fc += f";[v0][1:v]overlay=0:0[v1]"; last = "v1"
    run(cmd + ["-filter_complex", fc + f";[{last}]format=yuv420p[v]", "-map", "[v]", *ENC, "-t", str(d), out])


def seg_phone(out, src, ss, d, bg, mask):
    fc = (f"[0:v]fps=30,scale={PH_W}:{PH_H}:force_original_aspect_ratio=increase:flags=lanczos,crop={PH_W}:{PH_H}:0:0,format=rgba[s];"
          f"[2:v]format=gray[m];[s][m]alphamerge[sm];[1:v][sm]overlay={PH_X}:{PH_Y},format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(d), "-i", src, "-loop", "1", "-t", str(d), "-i", bg,
         "-loop", "1", "-t", str(d), "-i", mask, "-filter_complex", fc, "-map", "[v]", *ENC, "-t", str(d), out])


def seg_frames(out, framedir, d):
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(framedir, "f%04d.jpg"), *ENC, "-t", str(d), out])


def seg_qw_end(out, d=3.0):
    fc = ("[0:v]scale=1080:1920:flags=lanczos,format=rgba,fps=30,"
          "scale=eval=frame:w='trunc(1080*(1+0.06*max(0\\,1-t/0.2)+0.012*t)/2)*2':h='trunc(1920*(1+0.06*max(0\\,1-t/0.2)+0.012*t)/2)*2':flags=lanczos,"
          "crop=1080:1920,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(d), "-i", QW_END, "-filter_complex", fc, "-map", "[v]", *ENC, "-t", str(d), out])


def seg_dos_end(out, d=3.45):
    run(["ffmpeg", "-v", "error", "-y", "-ss", "17.05", "-t", str(d), "-i", DOS_REEL, "-vf", "fps=30,format=yuv420p", *ENC, "-t", str(d), out])


# ---------- reels ----------
T = lambda i: INDEX[("tim", i)]
J = lambda i: INDEX[("jc", i)]
DOS = lambda n: os.path.join(FOOT, "dos", n + ".mp4")
PILL99 = "What's in a $99 QuickWash"

REELS = {
    # Q02 — "What $99 gets you"
    "qw-99-whats-included": [
        ("clip", T(57), 0.8, 1.5, dict(pill="Everything in a\n$99 QuickWash")),
        ("clip", T(42), 3.2, 1.6, dict(pill="Everything in a\n$99 QuickWash")),
        ("clip", T(47), 2.6, 1.3, dict(text="We come to you", pill=PILL99)),
        ("clip", T(44), 0.6, 1.4, dict(text="Our own water and power", pill=PILL99)),
        ("clip", T(22), 3.0, 1.2, dict(text="Foam pre-soak", check=True, pill=PILL99)),
        ("clip", T(17), 1.2, 1.1, dict(text="Full hand wash", check=True, pill=PILL99)),
        ("clip", T(16), 0.8, 1.0, dict(text="Wheels cleaned", check=True, pill=PILL99)),
        ("clip", T(84), 6.0, 1.1, dict(text="Tires shined", check=True, pill=PILL99)),
        ("clip", T(98), 2.0, 1.1, dict(text="Interior vacuumed", check=True, pill=PILL99)),
        ("clip", T(96), 3.0, 1.2, dict(text="Dash to doors wiped down", check=True, pill=PILL99)),
        ("clip", T(33), 0.8, 1.6, dict(text="Windows, in and out", check=True, pill=PILL99)),
        ("clip", T(106), 0.5, 1.1, dict(text="Ceramic spray wax", check=True, pill=PILL99)),
        ("clip", T(103), 0.5, 1.1, dict(text="Ceramic spray wax", check=True, pill=PILL99)),
        ("clip", T(110), 1.5, 1.2, dict(text="Book in under 20 seconds")),
        ("clip", T(101), 0.6, 1.1, dict(text="Book in under 20 seconds")),
        ("qw_end", 3.0),
    ],
    # Q01 — "Dirty"
    "qw-dirty": [
        ("clip", J(29), 2.6, 2.0, dict(pill="Someone wrote “Dirty”\non this car")),
        ("clip", J(41), 3.6, 0.9, dict(text="Fair.")),
        ("clip", J(45), 0.6, 1.4, dict(text="So we came to it")),
        ("clip", J(20), 2.5, 0.9, dict(text="Foam.")),
        ("clip", J(13), 6.0, 0.9, dict(text="Hand wash.")),
        ("clip", J(57), 4.0, 0.9, dict(text="Full interior.")),
        ("clip", J(61), 4.0, 1.9, dict(text="On a rooftop in Jersey City")),
        ("clip", J(60), 5.0, 1.3, dict(text="QuickWash comes to you")),
        ("clip", J(38), 2.2, 1.1, dict(text="QuickWash comes to you")),
        ("qw_end", 3.0),
    ],
    # D03 — "Your storefront vs your DMs"
    "dos-storefront-vs-dms": [
        ("dms", 4.6, [(0.35, "How much for an SUV?"), (1.5, "u do interiors??"), (2.45, "price for 3 rows"), (3.3, "You free Saturday?")], "Every day. Same DMs."),
        ("phone", DOS("storefront"), 0.2, 2.0, ("Now I send", "one link.")),
        ("phone", DOS("storefront"), 7.5, 2.2, ("My packages.", "My prices.")),
        ("phone", DOS("storefront"), 21.5, 1.6, ("My add-ons.", None)),
        ("phone", DOS("storefront"), 50.2, 2.2, ("They pick a time", "and pay.")),
        ("clip", T(85), 1.5, 1.1, dict(text="Stop typing.")),
        ("clip", T(16), 0.8, 1.1, dict(text="Start detailing.")),
        ("dos_end", 3.45),
    ],
    # D06 — "Book your regulars by text"
    "dos-book-your-regulars": [
        ("clip", T(2), 1.0, 1.7, dict(pill="“Can you do a full detail\nThursday?”")),
        ("clip", T(1), 1.5, 1.8, dict(pill="“Can you do a full detail\nThursday?”")),
        ("clip", T(41), 1.0, 1.7, dict(text="Booked from the driveway")),
        ("phone", DOS("booking"), 8.7, 1.2, ("Package.", None)),
        ("phone", DOS("booking"), 11.6, 1.2, ("Date.", None)),
        ("phone", DOS("booking"), 13.4, 1.0, ("Invoice link.", "Done.")),
        ("phone", DOS("booking"), 23.6, 1.0, ("He gets a text.", "He pays.")),
        ("clip", T(81), 1.0, 1.0, dict(text="I keep working.")),
        ("dos_end", 3.45),
    ],
}

if __name__ == "__main__":
    for name, segs in REELS.items():
        if ONLY and name not in ONLY:
            continue
        wd = os.path.join(WORK, name); os.makedirs(wd, exist_ok=True)
        mask = os.path.join(wd, "mask.png"); phone_mask(mask)
        files, t = [], 0.0
        for i, s in enumerate(segs):
            out = os.path.join(wd, f"{i:02d}.mp4"); kind = s[0]
            if kind == "clip":
                _, src, ss, d, cap = s; png = os.path.join(wd, f"cap{i:02d}.png"); cap_png(png, **cap); seg_clip(out, src, ss, d, png)
            elif kind == "phone":
                _, src, ss, d, (h1, h2) = s; bg = os.path.join(wd, f"bg{i:02d}.png"); phone_bg(bg, h1, h2); seg_phone(out, src, ss, d, bg, mask)
            elif kind == "dms":
                _, d, bubbles, head = s; fd = os.path.join(wd, "dms"); dm_frames(fd, d, bubbles, head); seg_frames(out, fd, d)
            elif kind == "qw_end":
                d = s[1]; seg_qw_end(out, d)
            elif kind == "dos_end":
                d = s[1]; seg_dos_end(out, d)
            print(f"{name} {i:02d} {kind:8s} start={t:5.2f} dur={d}"); t += d; files.append(out)
        lst = os.path.join(wd, "list.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(wd, "video.mp4")])
        print(f"{name} total {t:.2f}s")
