"""Lift each still's headline (and the QuickWash badge) onto its own layer and fill the gap behind it.
usage: python3 tools/mklayers.py   (run from the reel folder)"""
import json
import numpy as np
from PIL import Image

L = {
    "mess":   {"h1": (99, 102, 859, 215), "h2": (271, 221, 686, 343)},
    "mind":   {"h1": (45, 161, 899, 249), "h2": (72, 268, 879, 358)},
    "reset":  {"h1": (116, 84, 816, 213), "h2": (73, 216, 880, 382)},
    "better": {"h1": (150, 70, 790, 215), "h2": (150, 215, 800, 350)},
    "effect": {"h1": (35, 133, 904, 243), "h2": (35, 243, 904, 434)},
    "fresh":  {"h1": (47, 129, 908, 230), "h2": (72, 246, 897, 387), "badge": (176, 1190, 764, 1400)},
}
PAD = 14


def box(x, r):
    for ax in (0, 1):
        pad = [(0, 0)] * x.ndim; pad[ax] = (r + 1, r)
        c = np.cumsum(np.pad(x, pad, mode="edge"), axis=ax)
        x = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return x


def gblur(x, r):
    for _ in range(3):
        x = box(x, max(1, r // 2))
    return x


meta = {}
for s, els in L.items():
    try:
        im = Image.open(f"assets/src/{s}.png").convert("RGB")
    except FileNotFoundError:
        continue
    a = np.asarray(im).astype(np.float32); H, W = a.shape[:2]; mask = np.ones((H, W), np.float32); meta[s] = {}
    boxes = {n: (max(0, x0 - PAD), max(0, y0 - PAD), min(W, x1 + PAD), min(H, y1 + PAD)) for n, (x0, y0, x1, y1) in els.items()}
    for (x0, y0, x1, y1) in boxes.values():
        mask[y0:y1, x0:x1] = 0
    src = a * mask[..., None]; plate = a.copy(); done = mask.copy()
    for r in (8, 16, 32, 64, 128, 256, 512):
        mb = gblur(mask, r); est = gblur(src, r) / np.maximum(mb, 1e-6)[..., None]
        sel = (done < 0.5) & ((mb > 0.18) | (r == 512)); plate[sel] = est[sel]; done[sel] = 1
    sm = gblur(plate.clip(0, 255), 10); hole = mask < 0.5; plate[hole] = sm[hole]
    Image.fromarray(plate.clip(0, 255).astype(np.uint8)).save(f"assets/layers/{s}_plate.jpg", quality=95)
    for n, (x0, y0, x1, y1) in boxes.items():
        crop = np.asarray(im.crop((x0, y0, x1, y1)).convert("RGBA")).copy(); h, w = crop.shape[:2]
        # keep only the lettering (and its soft shadow): alpha from difference to the filled plate
        diff = np.abs(crop[..., :3].astype(np.float32) - plate[y0:y1, x0:x1]).max(axis=2)
        al = np.clip((diff - 6) / 22, 0, 1) if n != "badge" else np.ones((h, w), np.float32)
        f = 8
        for i in range(f):
            v = (i + 1) / (f + 1); al[i, :] *= v; al[h - 1 - i, :] *= v; al[:, i] *= v; al[:, w - 1 - i] *= v
        crop[..., 3] = (al * 255).astype(np.uint8); Image.fromarray(crop).save(f"assets/layers/{s}_{n}.png")
        meta[s][n] = [x0, y0, x1 - x0, y1 - y0]
json.dump(meta, open("assets/layers/meta.json", "w")); print(json.dumps(meta))

# touch-ups: flat orange behind the blob headlines; round the badge's corners
from PIL import ImageDraw
for s in ("mess", "better"):
    if s in meta:
        p = Image.open(f"assets/layers/{s}_plate.jpg"); arr = np.asarray(p).copy(); src = np.asarray(Image.open(f"assets/src/{s}.png").convert("RGB"))
        for n in ("h1", "h2"):
            x, y, w, h = meta[s][n]; reg = src[y:y + h, x:x + w].reshape(-1, 3).astype(int)
            org = reg[(reg[:, 0] > 215) & (reg[:, 1] > 60) & (reg[:, 1] < 150) & (reg[:, 2] < 70)]
            arr[y:y + h, x:x + w] = np.median(org, axis=0).astype(np.uint8)
        out = Image.fromarray(arr); m = Image.new("L", out.size, 0); d = ImageDraw.Draw(m)
        for n in ("h1", "h2"):
            x, y, w, h = meta[s][n]; d.rectangle((x - 4, y - 4, x + w + 4, y + h + 4), fill=255)
        from PIL import ImageFilter
        soft = out.filter(ImageFilter.GaussianBlur(5)); out.paste(soft, (0, 0), m.filter(ImageFilter.GaussianBlur(4))); out.save(f"assets/layers/{s}_plate.jpg", quality=95)
if "fresh" in meta:
    b = Image.open("assets/layers/fresh_badge.png").convert("RGBA"); w, h = b.size
    big = Image.new("L", (w * 4, h * 4), 0); ImageDraw.Draw(big).rounded_rectangle((18 * 4, 16 * 4, (w - 18) * 4, (h - 16) * 4), 36 * 4, fill=255)
    b.putalpha(big.resize((w, h), Image.LANCZOS)); b.save("assets/layers/fresh_badge.png")
