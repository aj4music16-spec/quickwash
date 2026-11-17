"""Plan the v2 voiceover: place each beat's take on the film timeline from Scribe word onsets, and derive the cue sheet the
picture is timed to.  Usage: python3 -I tools/vo_plan.py  -> tools/cues.json (+ printed table)
Main voice (Liam): each beat starts at an anchor time that follows the picture rules below; inside a beat the take plays as
spoken, except pauses between phrases longer than the beat's cap are shortened to the cap (cut in the silence; never a
time-stretch). The alt voice (Jessica) is split at its phrase boundaries and each phrase is placed so that its cue word lands
on the main voice's time for the same word, so both cuts share one picture."""
import json, os, re
D = os.path.join(os.path.dirname(__file__), "..", "assets", "audio", "vo3")
TAKES = {"liam": ["b1_t2", "b2_t2", "b3_t1", "b4_t3", "b5_t2", "b6_t2"],
         "jessica": ["b1_t2", "b2_t1", "b3_t1", "b4_t2", "b5_t2", "b6_t2"]}
# phrases per beat as (first word index, last word index, cue word index), word indices in the Scribe word list
PHRASES = [[(0, 7, 0)],                                                   # Okay, your car wash? It's an app now.
           [(0, 2, 2), (3, 5, 5), (6, 8, 8), (9, 10, 10), (11, 13, 12)],  # car / wash / time / booked / twenty
           [(0, 3, 0), (4, 5, 4), (6, 12, 9)],                            # Every / Right / repeat
           [(0, 5, 0)],                                                   # Then
           [(0, 0, 0), (1, 2, 2), (3, 4, 4), (5, 8, 7), (9, 11, 9)],      # Home / office / gym / golf / wherever
           [(0, 5, 0)]]                                                   # Quick(Wash)
CAP = [9, 0.35, 9, 9, 0.5, 9]
HOOK_END = 2.8

def words(voice, take):
    d = json.load(open(os.path.join(D, f"{voice}_{take}.words.json")))
    return [(re.sub(r"[^\w']", "", w["text"]), w["start"], w["end"]) for w in d["words"] if w.get("type") == "word"]

def segs_of(ws, phrases):
    out = []
    for k, (a, b, c) in enumerate(phrases):
        gap_in = ws[a][1] - ws[phrases[k - 1][1]][2] if k else 0.2
        gap_out = ws[phrases[k + 1][0]][1] - ws[b][2] if k + 1 < len(phrases) else 0.3
        out.append({"src_from": round(ws[a][1] - min(0.08, gap_in / 2), 3), "src_to": round(ws[b][2] + min(0.14, gap_out / 2), 3),
                    "first": ws[a][1], "last_end": ws[b][2], "cue_src": ws[c][1], "cue_word": ws[c][0], "gap_in": gap_in})
    return out

plan = {"liam": [], "jessica": []}; cues = []
# beat cuts (on the 0.1 s grid) and the main voice's first-word time in each beat:
# b1 0.25 after frame 0; b2 after the phone has landed; b3 once the garage screen is up; b4/b5 ~0.25 s after the cut; b6 0.3 s
BEATS = [0.0, 2.8, 9.3, 13.4, 14.9, 21.0]; FILM_END = 24.5
FIRST = [0.25, 3.15, 9.9, 13.65, 15.15, 21.3]
beat_starts = BEATS; speech_end = []
for b in range(6):
    ws = words("liam", TAKES["liam"][b]); segs = segs_of(ws, PHRASES[b])
    t = FIRST[b]
    for k, s in enumerate(segs):
        if k: t = t_last_end + min(s["gap_in"], CAP[b])
        off = t - s["first"]                     # film = src + off
        plan["liam"].append({"beat": b + 1, "file": f"liam_{TAKES['liam'][b]}", "src_from": s["src_from"], "src_to": s["src_to"], "at": round(s["src_from"] + off, 3)})
        cues.append({"beat": b + 1, "word": s["cue_word"], "t": round(s["cue_src"] + off, 3)})
        t_last_end = s["last_end"] + off
        for w in ws[PHRASES[b][k][0]:PHRASES[b][k][1] + 1]: cues[-1].setdefault("words", []).append((w[0], round(w[1] + off, 3)))
    speech_end.append(round(t_last_end, 3))
    nxt = BEATS[b + 1] if b < 5 else FILM_END
    assert t_last_end <= nxt - 0.1, f"b{b+1} speech ends {t_last_end:.2f}, next cut {nxt}"
    if b < 5: assert FIRST[b + 1] >= t_last_end + 0.25, f"b{b+2} starts {FIRST[b+1] - t_last_end:.2f} s after b{b+1}"
film_end = FILM_END

# alt voice: phrase by phrase onto the same cue times
ci = 0; jprev = 0.0; warn = []
for b in range(6):
    ws = words("jessica", TAKES["jessica"][b])
    for s in segs_of(ws, PHRASES[b]):
        at = cues[ci]["t"] - (s["cue_src"] - s["src_from"])
        if at < jprev + 0.03: warn.append(f"b{b+1} {s['cue_word']}: pushed {jprev + 0.03 - at:.2f} s"); at = jprev + 0.03
        plan["jessica"].append({"beat": b + 1, "file": f"jessica_{TAKES['jessica'][b]}", "src_from": s["src_from"], "src_to": s["src_to"], "at": round(at, 3),
                                "speech_end": round(at + s["last_end"] - s["src_from"], 3)})
        jprev = at + s["src_to"] - s["src_from"]; ci += 1
    # a longer alt line must still clear the next cut by 0.25 s: pull the whole beat earlier (never before its own cut)
    nxt = BEATS[b + 1] if b < 5 else FILM_END
    mine = [p for p in plan["jessica"] if p["beat"] == b + 1]
    over = mine[-1]["speech_end"] - (nxt - 0.1)
    if over > 0:
        room = mine[0]["at"] - (BEATS[b] + 0.03)
        sh = min(over, room)
        for p in mine: p["at"] = round(p["at"] - sh, 3); p["speech_end"] = round(p["speech_end"] - sh, 3)
        warn.append(f"b{b+1}: alt line {over:.2f} s too long, whole beat moved {sh:.2f} s earlier" + ("" if sh >= over else " (STILL LONG)"))

out = {"film_end": film_end, "beat_starts": beat_starts, "speech_end": speech_end, "cues": cues, "plan": plan, "alt_warnings": warn}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "cues.json"), "w"), indent=1)
print("beats", beat_starts, "end", film_end, "speech ends", speech_end)
for c in cues: print(f"b{c['beat']} {c['word']:9s} {c['t']:6.2f}  f{round(c['t']*30):4d}   " + " ".join(f"{w}@{t:.2f}" for w, t in c["words"]))
for v in plan:
    print(v, " ".join(f"[{p['at']:.2f}-{p['at'] + p['src_to'] - p['src_from']:.2f}]" for p in plan[v]))
print("alt warnings:", warn)
