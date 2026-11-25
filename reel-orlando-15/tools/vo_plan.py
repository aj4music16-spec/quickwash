"""Cue sheet for the 15 s cut of "The $99 QuickWash, Orlando": place Liam's takes on the music's beat grid and write tools/cues.json.
Usage: python3 -I tools/vo_plan.py

The bed (assets/audio/music/bed1_15.wav, tools/shorten_bed.py) is 110 BPM with beat 0 at 0.130 s (measured from its onset envelope). Every
picture cut sits on a beat (snapped to the 30 fps frame grid). Each section's line is placed so that its first word's onset
lands on the section's first cut; inside a line the pauses are kept or shortened inside the silence (never time-stretched).
Word onsets: ElevenLabs Scribe (<take>.words.json); a phrase-first word's onset is refined to the acoustic onset (10 ms
envelope crossing -40 dB), but never earlier than 1 frame before Scribe's start (as reel-race/tools/vo_plan.py)."""
import json, math, os, re, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "assets", "audio", "vo")
BPM, PHASE = 110.0, 0.130
beat = lambda k: PHASE + k * 60 / BPM
snap = lambda t: round(t * 30) / 30
# shots: (id, first beat); the next shot starts where this one ends. END = beat of the end-card wipe.
SHOTS = [("s01", 0), ("s02", 6.5), ("s03", 9), ("s04", 11), ("s05", 13), ("s06", 16), ("s07", 18), ("s08", 20), ("end", 23)]
# s01 open (grille + van) | s02 hand wash | s03 vacuum stand-in | s04 glass | s05 tires + jambs | s06 interior | s07 spray wax |
# s08 price | end card. "Hand" sits on the off-beat 6.5: the open line needs 3.3 s and a 0.3 s breath before the list.
END_HOLD = 3.0
MIN_SHOT = 33   # frames (1.1 s); a cut is pushed later by up to a frame if the grid would make a shot shorter
# phrases: (take, first word idx, last word idx, anchor) where anchor = beat number (first word's onset lands there) or
# ("cap", s) = follow the previous phrase with its natural pause, shortened to at most s.
# a 5th element nudges a line earlier: Scribe on the v1 render heard Glass/Tires 2.0 f and Spray 2.8 f after their cuts
PHRASES = [
    ("s1_t1", 0, 0, 0),                  # Orlando:
    ("s1_t1", 1, 5, ("cap", 0.15)),      # the ninety-nine dollar QuickWash.
    ("s1_t1", 6, 9, ("cap", 0.20)),      # We come to you.
    ("s2_t1", 0, 1, 6.5),                # Hand wash.                 (s02)
    ("s2_t1", 2, 2, 9),                  # Vacuum.                    (s03)
    ("s2_t1", 3, 3, 11, -1 / 30),        # Glass.                     (s04)
    ("s2_t1", 4, 7, 13, -1 / 30),        # Tires and door jambs.      (s05)
    ("s2_t1", 8, 8, 16),                 # Interior.                  (s06)
    ("s2_t1", 9, 10, 18, -1 / 30),       # Spray wax.                 (s07)
    ("s3_t1", 0, 1, 20),                 # Ninety-nine bucks.         (s08 price)
    ("s3_t1", 2, 5, 23),                 # Drop your info below.      (end card)
]

def envelope(take):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(D, f"{take}.mp3"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = 160
    return np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(x) - h, h)])

def words(take):
    d = json.load(open(os.path.join(D, f"{take}.words.json")))
    return [[re.sub(r"[^\w']", "", w["text"]), w["start"], w["end"]] for w in d["words"] if w.get("type") == "word"]

def acoustic_onset(take, t):
    e = envelope(take); k = int(t * 100); j = k
    while j > 0 and e[j - 1] > -40 and k - j < 30: j -= 1
    while e[j] <= -40 and j - k < 20: j += 1
    return max(j / 100, t - 1 / 30)

cuts = {}; prev_f = None
for sid, k in SHOTS:
    f = round(beat(k) * 30)
    if prev_f is not None and f - prev_f < MIN_SHOT: f = prev_f + MIN_SHOT
    cuts[sid] = f / 30; prev_f = f
CUTAT = {k: cuts[sid] for sid, k in SHOTS}
segs, wordt, prev = [], [], None
for n, (take, a, z, anchor, *nudge) in enumerate(PHRASES):
    ws = words(take); on = acoustic_onset(take, ws[a][1])
    if isinstance(anchor, tuple):
        gap = ws[a][1] - prev[1][prev[3]][2]
        t = prev[2] + min(gap, anchor[1])
    else:
        t = CUTAT.get(anchor, snap(beat(anchor))) + (nudge[0] if nudge else 0)
    off = t - on                                              # film time = source time + off
    before = ws[a - 1][2] if a > 0 else 0.0
    after = ws[z + 1][1] if z + 1 < len(ws) else ws[z][2] + 0.4
    sf = max(before + 0.5 * (on - before), on - 0.06) if a > 0 else max(0.0, on - 0.06)
    st = min(ws[z][2] + 0.12, ws[z][2] + 0.5 * (after - ws[z][2]))
    segs.append({"phrase": n, "file": take, "src_from": round(sf, 3), "src_to": round(st, 3), "at": round(sf + off, 3)})
    for i in range(a, z + 1):
        wordt.append((n, take, ws[i][0], round((on if i == a else ws[i][1]) + off, 3), round(ws[i][2] + off, 3)))
    prev = (take, ws, ws[z][2] + off, z)
    if n and isinstance(anchor, tuple) and segs[-2]["at"] + segs[-2]["src_to"] - segs[-2]["src_from"] > segs[-1]["at"]:
        segs[-2]["src_to"] = round(segs[-2]["src_from"] + segs[-1]["at"] - segs[-2]["at"], 3)   # butt-join inside the pause
    if n and segs[-2]["at"] + segs[-2]["src_to"] - segs[-2]["src_from"] > segs[-1]["at"] + 0.02:
        raise SystemExit(f"phrase {n} overlaps the previous one: {segs[-2]} {segs[-1]}")

cuts["s01"] = 0.0
film_end = round(cuts["end"] + END_HOLD, 4)
first = lambda n: next(w[3] for w in wordt if w[0] == n)
cues = {"Orlando": first(0), "We": first(2), "Hand": first(3), "Vacuum": first(4), "Glass": first(5), "Tires": first(6), "Interior": first(7),
        "Spray": first(8), "Ninety": first(9), "Drop": first(10)}
out = {"bpm": BPM, "phase": PHASE, "cuts": cuts, "cues": cues, "film_end": film_end, "segments": segs, "words": wordt}
json.dump(out, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
for k, v in cuts.items(): print(f"cut {k:4s} {v:7.3f} f{round(v * 30)}")
for k, v in cues.items(): print(f"cue {k:11s} {v:7.3f} f{v * 30:6.1f}")
print("film end", film_end, f"f{round(film_end * 30)}; speech ends", round(max(w[4] for w in wordt), 3))
