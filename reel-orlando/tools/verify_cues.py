"""Check a render against tools/cues.json: hard cuts found in the MP4 (frame-difference spikes) and the cue words' starts in a
Scribe transcript of the render's own audio.  Usage: python3 -I tools/verify_cues.py <render.mp4> <render.words.json>"""
import json, os, re, subprocess, sys
import numpy as np
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = json.load(open("tools/cues.json")); mp4, wj = os.path.abspath(sys.argv[1]), sys.argv[2]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "scale=108:192", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(np.float32); diff = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
cuts = [i for i in range(1, len(diff)) if diff[i] > 14 and diff[i] > 3 * np.median(diff[max(0, i - 6):i + 6])]
print("hard cuts in the render (frames):", cuts)
for k, t in C["cuts"].items():
    f = round(t * 30); near = min(cuts, key=lambda c: abs(c - f)) if cuts else None
    print(f"cut {k:4s} planned f{f:3d}  found f{near}  diff {near - f:+d}" if near is not None and abs(near - f) < 8 else f"cut {k:4s} planned f{f:3d}  (no hard cut found: {'wipe' if k == 'end' else 'first frame' if f == 0 else '?'})")
ws = [(re.sub(r"[^\w']", "", w["text"]).lower(), w["start"]) for w in json.load(open(wj))["words"] if w.get("type") == "word"]
WORD = {"Orlando": ("orlando", 1), "And": ("and", 1), "Foam": ("foam", 1), "Vacuum": ("vacuum", 1), "Glass": ("glass", 1), "Tire": ("tire", 1),
        "Interior": ("interior", 1), "All": ("all", 1), "Ninety": ("99", 2), "Orlando_cta": ("orlando", 2), "Drop": ("drop", 1)}
VIS = {"Orlando": "film start / chip + offer on frame 0", "And": "cut s02 + 'We come to you.'", "Foam": "cut s03 + row 1", "Vacuum": "cut s06 + row 2",
       "Glass": "cut s07 + row 3", "Tire": "cut s08 + row 4", "Interior": "cut s10 + row 5", "And_wax": "cut s11 + row 6", "All": "cut s12, rows to full",
       "Ninety": "cut s13 + '$99'", "Orlando_cta": "cut s14 + CTA line", "Drop": "end-card wipe starts"}
for k, t in C["cues"].items():
    if k not in VIS: continue
    CUT = {"Orlando": None, "And": "s02", "Foam": "s03", "Vacuum": "s06", "Glass": "s07", "Tire": "s08", "Interior": "s10", "And_wax": "s11",
           "All": "s12", "Ninety": "s13", "Orlando_cta": "s14", "Drop": "end"}
    vis = round(C["cuts"][CUT[k]] * 30) if CUT[k] else 0   # the picture event: the section's cut (the chip/offer are on from frame 0)
    if k == "And_wax":   # "and" is said many times: take the first one after "down"
        i = next(j for j, w in enumerate(ws) if w[0] == "down"); sp = ws[i + 1][1]
    else:
        w, n = WORD[k]; sp = [s for x, s in ws if x == w][n - 1]
    print(f"{k:12s} spoken f{sp * 30:6.1f} ({sp:6.3f})  visual f{vis:3d}  diff {vis - sp * 30:+5.1f}  {VIS[k]}")
