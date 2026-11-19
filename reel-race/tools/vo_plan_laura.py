"""Plan the Laura (main) voiceover and write tools/cues.json. Usage: python3 -I tools/vo_plan_laura.py
Scribe was unavailable (the ElevenLabs credit quota ran out), so phrase onsets come from the audio itself: speech segments are
where the 10 ms envelope is above -38 dB with gaps of >= 80 ms (the same split ffmpeg silencedetect makes), and each line's
phrases are known groups of those segments (checked against eleven_v3's own alignment). Every cue word is phrase-first, so
its onset is its segment's start. Pauses: inside b2, gaps between items are evened to 0.35 s minimum (she runs two items
together at 0.15 s) and nothing is time-stretched. b4 ("Booking it? Twenty seconds.") could not be generated (quota), so
the booking beat has no voice; its picture cues keep the Liam cut's rhythm (tap 0.3 s in, Booked 1.07 s in, 1.9 s beat)."""
import json, math, os, subprocess
import numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); D = "assets/audio/vo-laura"; os.chdir(ROOT)
TAKES = {1: "b1_t2", 2: "b2_t3", 3: "b3_t1", 5: "b5_t4"}
# phrases: (first word, its eleven_v3 alignment time in the take). The alignment is too loose to cue on (up to 0.4 s off),
# but it says which speech segment a phrase starts in: the first segment that starts no earlier than (alignment - 0.25 s).
PHRASES = {1: [("Everything", 0.39), ("Ready", 3.65), ("Go", 4.80)],
           2: [("Foam", 0.28), ("Vacuum", 1.31), ("seats", 2.21), ("Glass", 3.94), ("Tire", 5.33), ("Interior", 7.60), ("Ceramic", 8.96)],
           3: [("Ninety", 0.07), ("Done", 1.22), ("with", 1.60)],
           5: [("Quick", 0.20), ("Grab", 0.90)]}
MINGAP = {1: None, 2: 0.35, 3: None, 5: None}           # b2: even out the two run-together items
GO_GAP = 0.55

def segments(take):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{D}/{take}.mp3", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = 160
    on = np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-9) > -38 for i in range(0, len(x) - h, h)])
    segs = []; i = 0; n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or (j + 8 < n and on[j:j + 8].any())): j += 1   # bridge gaps under 80 ms
            if j - i >= 4: segs.append((i / 100, j / 100))
            i = j
        else: i += 1
    return segs

segs_out, words, T = [], [], {}
t_end = None; cue = {}
for b in (1, 2, 3, 5):
    sg = segments(TAKES[b]); starts = []
    for k, (name, al) in enumerate(PHRASES[b]):
        starts.append(0 if k == 0 else next(i for i, (a, z) in enumerate(sg) if a >= al - 0.25 and i > starts[-1]))
    ph = [(sg[i][0], sg[(starts[k + 1] if k + 1 < len(starts) else len(sg)) - 1][1], PHRASES[b][k][0]) for k, i in enumerate(starts)]
    if b == 1: first = 0.25
    elif b == 2: first = t_end + 0.55                     # "Foam" 0.55 s after "Go" ends: the race starts on it
    elif b == 3: first = t_end + 0.55                     # "Ninety-nine" -> payoff cut
    else: first = T["end_cut"] + 0.3                      # "QuickWash" 0.3 s into the end card
    t = first
    for k, (a, z, name) in enumerate(ph):
        if k:
            gap = a - ph[k - 1][1]
            if MINGAP[b]: gap = max(gap, MINGAP[b])
            if b == 1: gap = min(gap, 0.3)                    # hook: "one!" -> "Ready?" -> "Go!" tightened in the silences
            t = t_last + gap
        off = t - a
        gin = a - ph[k - 1][1] if k else 0.1; gout = ph[k + 1][0] - z if k + 1 < len(ph) else 0.25
        sf, st = max(0, a - min(0.03, gin / 2)), z + min(0.1, gout / 2)
        segs_out.append({"beat": b, "file": TAKES[b], "dir": D, "src_from": round(sf, 3), "src_to": round(st, 3), "at": round(sf + off, 3)})
        cue.setdefault(name, round(a + off, 3)); words.append((b, name, round(a + off, 3), round(z + off, 3)))
        t_last = z + off
    t_end = t_last; T[f"b{b}_end"] = round(t_end, 3)
    if b == 3:
        T["book_cut"] = round(t_end + 0.25, 3); T["end_cut"] = round(T["book_cut"] + 1.9, 3)
cues = {"Go": cue["Go"], "Foam": cue["Foam"], "Vacuum": cue["Vacuum"], "Glass": cue["Glass"], "Tire": cue["Tire"],
        "Interior": cue["Interior"], "Ceramic": cue["Ceramic"], "Ninety": cue["Ninety"], "Done": cue["Done"],
        "Booking": round(T["book_cut"] + 0.3, 3), "Twenty": round(T["book_cut"] + 1.0667, 3), "Quick": cue["Quick"], "Grab": cue["Grab"]}
cuts = {"race": cues["Foam"], "payoff": cues["Ninety"], "book": T["book_cut"], "end": T["end_cut"]}
film_end = round(math.ceil(max(cuts["end"] + 3.0, T["b5_end"] + 1.0) * 30 - 1e-6) / 30, 4)
out = {"voice": "laura", "cues": cues, "cuts": cuts, "film_end": film_end, "speech_end": T, "timer_stop": round(cues["Done"] - cues["Go"], 3),
       "segments": segs_out, "words": words, "no_vo": ["Booking", "Twenty"]}
json.dump(out, open("tools/cues.json", "w"), indent=1)
for k, v in cues.items(): print(f"{k:9s} {v:6.2f}  f{round(v * 30)}")
print("cuts", cuts, "end", film_end, "timer", out["timer_stop"]); print("speech", T)
print("phrases", [(w[1], w[2], w[3]) for w in words])
