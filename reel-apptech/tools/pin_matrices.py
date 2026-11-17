"""Turn the tracked screen corners (tools/track_phone.py output) into CSS matrix3d strings that map a 1320x2868 screenshot
onto the phone screen, one per 30 fps frame. The quad is grown 0.8% about its centre so the pin covers the anti-aliased
inner bezel edge. Usage: python3 -I tools/pin_matrices.py track.json  -> JS array literal on stdout (pasted into hook.html)."""
import json, sys
import numpy as np

W, H, GROW = 1320, 2868, 1.008
def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    h = np.linalg.solve(np.array(A, float), np.array([c for p in dst for c in p], float))
    return np.append(h, 1).reshape(3, 3)

rows = []
for q in json.load(open(sys.argv[1])):
    pts = np.array(q).reshape(4, 2); c = pts.mean(0); pts = c + (pts - c) * GROW
    a, b, cc, d, e, f, g, hh, _ = homography([(0, 0), (W, 0), (W, H), (0, H)], pts).ravel()
    m = [a, d, 0, g, b, e, 0, hh, 0, 0, 1, 0, cc, f, 0, 1]
    rows.append("matrix3d(" + ",".join(f"{v:.6g}" for v in m) + ")")
print("[" + ",\n".join(json.dumps(r) for r in rows) + "]")
