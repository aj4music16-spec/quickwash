"""Cue sheet for "The $99 QuickWash, Orlando": place Liam's takes on the music's beat grid and write tools/cues.json.
Usage: python3 -I tools/vo_plan.py

The bed (assets/audio/music/bed1_ext.wav) is 110 BPM with beat 0 at 0.130 s (measured from its onset envelope). Every
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
SHOTS = [("s01", 0), ("s02", 5), ("s03", 8), ("s04", 11), ("s05", 14), ("s06", 17), ("s07", 22), ("s08", 25), ("s09", 28),
         ("s10", 31), ("s11", 34), ("s12", 38), ("s13", 41), ("s14", 44), ("end", 48)]
END_HOLD = 4.0
# phrases: (take, first word idx, last word idx, anchor) where anchor = beat number (first word's onset lands there) or
# ("cap", s) = follow the previous phrase with its natural pause, shortened to at most s.
PHRASES = [
    ("open_t2", 0, 7, 0),             # Orlando, this is the ninety-nine dollar QuickWash.   (s01)
    ("open_t2", 8, 13, 5),            # And yeah, we come to you.                           (s02 cut on "And")
    ("list_t2", 0, 5, 8),             # Foam and a full hand wash.                          (foam section)
    ("list_t2", 6, 6, 17),            # Vacuum:                                             (vacuum section)
    ("list_t2", 7, 9, ("cap", 0.30)),  # seats, floors, trunk.
    ("list_t2", 10, 10, 22),          # Glass,                                              (glass section)
    ("list_t2", 11, 13, ("cap", 0.12)),  # inside and out.
    ("list_t2", 14, 18, 25),          # Tire shine and door jambs.                          (tires section)
    ("list_t2", 19, 21, 31),          # Interior wiped down.                                (interior section)
    ("list_t2", 22, 28, 34),          # And a ceramic spray wax to finish.                  (wax section)
    ("price_t1", 0, 5, 38, -1 / 30),  # All of it, in your driveway,  (result; 1 frame early: Scribe on the v1 render heard "All" 2.2 f after the cut)
    ("price_t1", 6, 7, 41),           # ninety-nine bucks.                                  (price shot, "$99")
    ("cta_t1", 0, 6, 44),             # Orlando spots are filling up this week.             (CTA)
    ("cta_t1", 7, 13, 48),            # Drop your info below and grab yours.                (end card)
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

segs, wordt, prev = [], [], None
for n, (take, a, z, anchor, *nudge) in enumerate(PHRASES):
    ws = words(take); on = acoustic_onset(take, ws[a][1])
    if isinstance(anchor, tuple):
        gap = ws[a][1] - prev[1][prev[3]][2]
        t = prev[2] + min(gap, anchor[1])
    else:
        t = snap(beat(anchor)) + (nudge[0] if nudge else 0)
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

cuts = {sid: snap(beat(k)) for sid, k in SHOTS}
film_end = round(cuts["end"] + END_HOLD, 4)
def cue(word, take, nth=1):
    hits = [w for w in wordt if w[1] == take and w[2].lower() == word.lower()]
    return hits[nth - 1][3]
cues = {"Orlando": cue("Orlando", "open_t2"), "And": cue("And", "open_t2"), "we": cue("we", "open_t2"),
        "Foam": cue("Foam", "list_t2"), "Vacuum": cue("Vacuum", "list_t2"), "Glass": cue("Glass", "list_t2"),
        "Tire": cue("Tire", "list_t2"), "Interior": cue("Interior", "list_t2"), "And_wax": next(w[3] for w in wordt if w[0] == 9),
        "All": cue("All", "price_t1"), "Ninety": cue("99", "price_t1"), "Orlando_cta": cue("Orlando", "cta_t1"),
        "Drop": cue("Drop", "cta_t1")}
out = {"bpm": BPM, "phase": PHASE, "cuts": cuts, "cues": cues, "film_end": film_end, "segments": segs, "words": wordt}
json.dump(out, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
for k, v in cuts.items(): print(f"cut {k:4s} {v:7.3f} f{round(v * 30)}")
for k, v in cues.items(): print(f"cue {k:11s} {v:7.3f} f{v * 30:6.1f}")
print("film end", film_end, f"f{round(film_end * 30)}; speech ends", round(max(w[4] for w in wordt), 3))
