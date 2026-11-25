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
WORD = {"Orlando": ("orlando", 1), "We": ("we", 1), "Hand": ("hand", 1), "Vacuum": ("vacuum", 1), "Glass": ("glass", 1), "Tires": ("tires", 1),
        "Interior": ("interior", 1), "Spray": ("spray", 1), "Ninety": ("99", 2), "Drop": ("drop", 1)}
CUT = {"Orlando": None, "We": None, "Hand": "s02", "Vacuum": "s03", "Glass": "s04", "Tires": "s05", "Interior": "s06", "Spray": "s07",
       "Ninety": "s08", "Drop": "end"}
for k, t in C["cues"].items():
    w, n = WORD[k]; sp = [s for x, s in ws if x == w][n - 1]
    vis = round(C["cuts"][CUT[k]] * 30) if CUT[k] else (0 if k == "Orlando" else round(t * 30))
    what = {"Orlando": "chip + offer on frame 0", "We": "'We come to you.' lands", "end": "end-card wipe"}.get(k, f"cut {CUT[k]} + checklist row" if k != "Ninety" else "cut s08 + '$99'")
    if k == "Drop": what = "end-card wipe starts"
    print(f"{k:9s} spoken f{sp * 30:6.1f}  visual f{vis:3d}  diff {vis - sp * 30:+5.1f}  {what}")
