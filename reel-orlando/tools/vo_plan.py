"""Place the Orlando voiceover on the film timeline from Scribe word onsets and write tools/cues.json (the picture's cue
sheet).  Usage: python3 -I tools/vo_plan.py
Each beat's take plays as spoken, except that pauses between phrases longer than the cap are shortened inside the silence
(never a time-stretch). Phrase-first onsets are refined to the acoustic onset (10 ms envelope crossing -40 dB) but never
earlier than 1 frame before Scribe's word start (as reel-race/tools/vo_plan.py). Cues are floored to the frame grid."""
import json, math, os, re, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "assets", "audio", "vo")
TAKES = ["b1_t1", "b2_t2", "b3_t1", "b4_t1", "b5_t1"]
# phrases (first word, last word) as Scribe word indices; CAP = longest pause kept before each phrase
PHRASES = [[(0, 0), (1, 9)],                                   # Orlando. / Still burning ... line?
           [(0, 6), (7, 13)],                                  # QuickWash ... instead. / You don't even have to come outside.
           [(0, 4), (5, 5), (6, 6), (7, 7), (8, 10), (11, 12)],  # Foam and a hand wash / vacuum / glass / tires / interior wipe-down / spray wax
           [(0, 2), (3, 4)],                                   # All of it. / Ninety-nine bucks.
           [(0, 7), (8, 14)]]                                  # Spots ... week. / Drop your info below and grab yours.
CAP = [[0, 0.3], [0, 0.3], [0, 0.55, 0.5, 0.5, 0.5, 0.5], [0, 0.35], [0, 0.34]]
GAP = [0.2, 0.35, 0.4, 0.35, 0.45]   # b1: first word at 0.2 s; then the pause before each beat's first word

def envelope(take):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(D, f"{take}.mp3"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = 160
    return np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(x) - h, h)])

def words(take, firsts=()):
    d = json.load(open(os.path.join(D, f"{take}.words.json")))
    ws = [[re.sub(r"[^\w']", "", w["text"]), w["start"], w["end"]] for w in d["words"] if w.get("type") == "word"]
    e = envelope(take)
    for i in firsts:
        k = int(ws[i][1] * 100); j = k
        while j > 0 and e[j - 1] > -40 and k - j < 30: j -= 1
        while e[j] <= -40 and j - k < 20: j += 1
        ws[i][1] = j / 100
    return [tuple(w) for w in ws]

segs = []; T = {}; wordt = []; t_end = 0
for b, take in enumerate(TAKES):
    ws = words(take, [a for a, z in PHRASES[b]]); raw = words(take)
    t = GAP[b] if b == 0 else t_end + GAP[b]
    for k, (a, z) in enumerate(PHRASES[b]):
        if k: t = t_last + min(ws[a][1] - ws[PHRASES[b][k - 1][1]][2], CAP[b][k])
        off = t - ws[a][1]
        gi = ws[a][1] - ws[PHRASES[b][k - 1][1]][2] if k else 0.2
        go = ws[PHRASES[b][k + 1][0]][1] - ws[z][2] if k + 1 < len(PHRASES[b]) else 0.3
        sf, st = max(0, ws[a][1] - min(0.04, gi / 2)), ws[z][2] + min(0.12, go / 2)
        segs.append({"beat": b + 1, "file": take, "src_from": round(sf, 3), "src_to": round(st, 3), "at": round(sf + off, 3)})
        for i, w in enumerate(ws[a:z + 1]):
            t0 = w[1] + off
            if i == 0: t0 = max(t0, raw[a][1] + off - 1 / 30)
            else: t0 = raw[a + i][1] + off
            wordt.append((b + 1, w[0], round(t0, 3), round(w[2] + off, 3)))
        t_last = ws[z][2] + off
    t_end = t_last; T[f"b{b+1}_end"] = round(t_end, 3)

fl = lambda t: round(math.floor(t * 30 + 1e-6) / 30, 4)
def at(word, beat):
    return fl(next(w[2] for w in wordt if w[0] == beat and w[1].lower() == word.lower()))
cues = {"Orlando": at("Orlando", 1), "Quick": at("Quick", 2), "instead": at("instead", 2), "dont": at("don't", 2),
        "Foam": at("Foam", 3), "vacuum": at("vacuum", 3), "glass": at("glass", 3), "tires": at("tires", 3),
        "interior": at("interior", 3), "spray": at("spray", 3), "All": at("All", 4), "Ninety": at("99", 4),
        "Spots": at("Spots", 5), "Drop": at("Drop", 5)}
film_end = round(math.ceil((cues["Drop"] + 4.1) * 30 - 1e-6) / 30, 4)
out = {"cues": cues, "film_end": film_end, "speech_end": T, "segments": segs, "words": wordt}
json.dump(out, open(os.path.join(HERE, "cues.json"), "w"), indent=1)
for k, v in cues.items(): print(f"{k:9s} {v:6.3f}  f{round(v * 30)}")
print("end", film_end, f"f{round(film_end * 30)}", "speech ends", T)
c = [cues[k] for k in ("Quick", "instead", "Foam", "vacuum", "tires", "spray", "Spots", "Drop")] + [film_end]
print("shot lengths", [round(b - a, 2) for a, b in zip(c, c[1:])])
