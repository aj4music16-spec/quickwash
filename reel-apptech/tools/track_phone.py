"""Track the inner screen of the floating phone in assets/footage/hook-phone.mp4 (c14 0-2.4 s, 1080x1920, 30 fps).
Usage: python3 -I tools/track_phone.py assets/footage/hook-phone.mp4 > compositions/_track.json
Per frame: bright pixels (grey > 215, eroded 3 px before the fill and regrown after) connected to a seed inside the screen = the screen (the black bezel ring cuts it from the
white backdrop). Left, right and bottom are least-squares line through the component's boundary over the middle 70% of that side
(skipping the rounded corners); the four corners are the line intersections. Output: [[x0,y0,x1,y1,x2,y2,x3,y3], ...] TL TR BR BL."""
import json, subprocess, sys
import numpy as np

SRC = sys.argv[1]; W, H = 1080, 1920
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W)

def component(mask, seed):
    reg = np.zeros_like(mask); reg[seed[1], seed[0]] = True
    while True:
        g = reg.copy()
        g[1:] |= reg[:-1]; g[:-1] |= reg[1:]; g[:, 1:] |= reg[:, :-1]; g[:, :-1] |= reg[:, 1:]
        g &= mask
        if g.sum() == reg.sum(): return reg
        reg = g

def fit(ps):  # line through points as (point, direction)
    ps = np.asarray(ps, float); c = ps.mean(0); _, _, vt = np.linalg.svd(ps - c); return c, vt[0]

def meet(l1, l2):
    (p, d), (q, e) = l1, l2
    t = np.linalg.solve(np.array([d, -e]).T, q - p); return p + t[0] * d

out = []; prev = None
for f in frames:
    small = f[::2, ::2] > 215
    er = small.copy()  # erode 3 px (half res) so thin bright gaps in the bezel cannot leak the fill into the backdrop
    for _ in range(3):
        e = er.copy(); e[1:] &= er[:-1]; e[:-1] &= er[1:]; e[:, 1:] &= er[:, :-1]; e[:, :-1] &= er[:, 1:]; er = e
    seed = (280, 700) if prev is None else (int((prev[0] + prev[4]) / 4), int((prev[1] + prev[5]) / 4 + 150))
    comp = component(er, seed)
    for _ in range(3):
        g = comp.copy(); g[1:] |= comp[:-1]; g[:-1] |= comp[1:]; g[:, 1:] |= comp[:, :-1]; g[:, :-1] |= comp[:, 1:]; comp = g & small
    full = np.kron(comp, np.ones((2, 2), bool)) & (f > 215)
    ys, xs = np.where(full); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    L, R, T, B = [], [], [], []
    for y in range(int(y0 + 0.15 * (y1 - y0)), int(y1 - 0.15 * (y1 - y0))):
        row = np.where(full[y])[0]
        if row.size: L.append((row.min(), y)); R.append((row.max() + 1, y))
    for x in range(int(x0 + 0.15 * (x1 - x0)), int(x1 - 0.15 * (x1 - x0))):
        col = np.where(full[:, x])[0]
        if col.size: B.append((x, col.max() + 1))
    # top edge: the fill is unreliable there (the Dynamic Island splits it), so walk down each column beside the island
    # (18-32% and 68-82% of the width) from the backdrop: past the first black bezel pixel (< 80), the first bright pixel (> 200).
    for fr in [*np.arange(0.18, 0.32, 0.01), *np.arange(0.68, 0.82, 0.01)]:
        x = int(x0 + fr * (x1 - x0)); col = f[:, x]
        dark = np.where(col[40:1200] < 80)[0]
        if not dark.size: continue
        yd = 40 + dark[0]; br = np.where(col[yd:yd + 200] > 200)[0]
        if br.size: T.append((x, yd + br[0]))
    l, r, t, b = fit(L), fit(R), fit(T), fit(B)
    q = [meet(t, l), meet(t, r), meet(b, r), meet(b, l)]
    prev = [float(v) for p in q for v in p]; out.append(prev)
# light temporal smoothing (centred 3-tap) against per-frame edge jitter
o = np.array(out); sm = o.copy(); sm[1:-1] = (o[:-2] + 2 * o[1:-1] + o[2:]) / 4
print(json.dumps([[round(float(v), 1) for v in r] for r in sm]))
