"""Place the reel-race voiceover on the film timeline from Scribe word onsets and write tools/cues.json (the picture's cue
sheet).  Usage: python3 -I tools/vo_plan.py
Each beat's take plays as spoken except that pauses between phrases longer than the cap are shortened inside the silence
(never a time-stretch). Beat cuts follow the words: the race starts on "Foam", each shot on its item's first word, the
payoff on "Ninety-nine", the booking beat 0.25 s after b3 ends, the end card 0.3 s after b4 ends."""
import json, math, os, re, subprocess
import numpy as np
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio", "vo")
TAKES = ["b1_t1", "b2_t1", "b3_t1", "b4_t1", "b5_t2"]
# phrases: (first word, last word, cue word) indices into the Scribe word list; cap = longest pause kept before the phrase
PHRASES = [[(0, 13, 0), (14, 14, 14), (15, 15, 15)],                       # Everything ... one. / Ready? / Go
           [(0, 4, 0), (5, 5, 5), (6, 8, 6), (9, 12, 9), (13, 17, 13), (18, 20, 18), (21, 23, 21)],  # Foam / Vacuum: / seats.. / Glass / Tire / Interior / Ceramic
           [(0, 1, 0), (2, 2, 2), (3, 6, 3)],                                # Ninety-nine bucks. / Done, / with time to spare.
           [(0, 1, 0), (2, 3, 2)],                                           # Booking it? / Twenty seconds.
           [(0, 4, 0)]]                                                      # QuickWash. Grab the app.
CAP = [[0, 0.15, 0.3], [0, 0.55, 0.5, 0.55, 0.55, 0.55, 0.55], [0, 0.45, 0.2], [0, 0.3], [0]]

def envelope(take):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(D, f"{take}.mp3"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = 160
    return np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(x) - h, h)])

def words(take, firsts=()):
    """Scribe words; for phrase-first words the onset is refined to where the voice actually starts (10 ms envelope crosses
    -40 dB): Scribe puts some onsets late (b3 "Ninety-nine" by 0.17 s), which would clip the word and late-cue the cut."""
    d = json.load(open(os.path.join(D, f"{take}.words.json")))
    ws = [[re.sub(r"[^\w']", "", w["text"]), w["start"], w["end"]] for w in d["words"] if w.get("type") == "word"]
    e = envelope(take)
    for i in firsts:
        k = int(ws[i][1] * 100); j = k
        while j > 0 and e[j - 1] > -40 and k - j < 30: j -= 1
        while e[j] <= -40 and j - k < 20: j += 1
        ws[i][1] = j / 100
    return [tuple(w) for w in ws]

segs = []; T = {}; wordt = []
t_end = None
for b, take in enumerate(TAKES):
    ws = words(take, [a for a, z, c in PHRASES[b]]); raw = words(take)
    if b == 0: first = 0.25
    elif b == 1: first = t_end + 0.4                       # "Foam" 0.4 s after "Go" ends: the race starts on it
    elif b == 2: first = t_end + 0.3                       # "Ninety-nine" -> payoff cut
    elif b == 3: first = t_end + 0.15 + 0.3                # booking cut at b3 end + 0.15; phone lands in 0.3
    else: first = t_end + 0.25 + 0.3                       # end card at b4 end + 0.25; "QuickWash" 0.3 s in
    t = first
    for k, (a, z, c) in enumerate(PHRASES[b]):
        if k: t = t_last + min(ws[a][1] - ws[PHRASES[b][k - 1][1]][2], CAP[b][k])
        off = t - ws[a][1]
        gi = ws[a][1] - ws[PHRASES[b][k - 1][1]][2] if k else 0.2
        go = ws[PHRASES[b][k + 1][0]][1] - ws[z][2] if k + 1 < len(PHRASES[b]) else 0.3
        sf, st = ws[a][1] - min(0.04, gi / 2), ws[z][2] + min(0.12, go / 2)
        segs.append({"beat": b + 1, "file": take, "src_from": round(sf, 3), "src_to": round(st, 3), "at": round(sf + off, 3)})
        for i, w in enumerate(ws[a:z + 1]):
            t0 = w[1] + off
            # cue time for a phrase-first word: its acoustic onset, but no earlier than 1 frame before Scribe's estimate
            # (they differ by up to 0.17 s on "Ninety-nine", where the nasal "N" starts well before Scribe's word start)
            if i == 0: t0 = max(t0, raw[a][1] + off - 1 / 30)
            wordt.append((b + 1, w[0], round(t0, 3), round(w[2] + off, 3)))
        t_last = ws[z][2] + off
    t_end = t_last
    T[f"b{b+1}_end"] = round(t_end, 3)

def at(word, n=1, beat=None):
    hits = [w for w in wordt if w[1].lower() == word.lower() and (beat is None or w[0] == beat)]
    return hits[n - 1][2]
cues = {"Go": at("Go"), "Foam": at("Foam"), "Vacuum": at("Vacuum"), "Glass": at("Glass"), "Tire": at("Tire"),
        "Interior": at("Interior"), "Ceramic": at("Ceramic"), "Ninety": wordt[[w[0] for w in wordt].index(3)][2],
        "Done": at("Done"), "Booking": at("Booking"), "Twenty": [w for w in wordt if w[0] == 4][2][2], "Quick": [w for w in wordt if w[0] == 5][0][2],
        "Grab": at("Grab")}
cuts = {"race": cues["Foam"], "payoff": cues["Ninety"], "book": round(T["b3_end"] + 0.15, 3), "end": round(T["b4_end"] + 0.25, 3)}
film_end = round(math.ceil(max(cuts["end"] + 3.0, T["b5_end"] + 1.0) * 30 - 1e-6) / 30, 4)   # on the frame grid
out = {"cues": cues, "cuts": cuts, "film_end": film_end, "speech_end": T, "timer_stop": round(cues["Done"] - cues["Go"], 3), "segments": segs, "words": wordt}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cues.json"), "w"), indent=1)
for k, v in cues.items(): print(f"{k:9s} {v:6.2f}  f{round(v * 30)}")
print("cuts", cuts, "end", film_end, "timer stops at", out["timer_stop"])
print("speech ends", T)
print("item shot lengths", [round(b - a, 2) for a, b in zip([cues[k] for k in ("Foam","Vacuum","Glass","Tire","Interior","Ceramic")], [cues[k] for k in ("Vacuum","Glass","Tire","Interior","Ceramic","Ninety")])])
