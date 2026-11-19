"""v3 cue sheet for the main (Liam) cut: start from tools/cues-liam.json (Liam's placed VO, tools/vo_plan.py) and
 1. add the two mid-line cuts that make every phrase show its own action: "hand" (foam cannon -> mitt hand wash) and
    "door" (tire spray -> door jamb); Scribe word starts, taken one frame early like the other cues (floor to the frame);
 2. insert the WashClub beat (2.6 s, light background) at the old booking cut and shift everything after it: the booking
    beat, the end card, Liam's b4/b5 VO segments and their cues;
 3. reserve the VO slot "b3b" for the line "And if you join WashClub? Sixty-nine." 0.2 s into the WashClub beat; "Sixty" is the
    $69 cue (planned 0.75 s into the beat until the line exists; see SPEC.md "Pickup lines").
Usage: python3 -I tools/cues_v3.py  -> tools/cues.json"""
import json, math, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = json.load(open("tools/cues-liam.json")); WC = 2.6
fl = lambda t: math.floor(t * 30 + 1e-6) / 30
w = {(x[0], x[1].lower()): x[2] for x in C["words"]}
C["cues"]["hand"] = round(fl(w[(2, "hand")]), 4); C["cues"]["door"] = round(fl(w[(2, "door")]), 4)
old_book = C["cuts"]["book"]; C["cuts"]["washclub"] = old_book
for k in ("Booking", "Twenty", "Quick", "Grab"): C["cues"][k] = round(C["cues"][k] + WC, 4)
for k in ("book", "end"): C["cuts"][k] = round(C["cuts"][k] + WC, 4)
for s in C["segments"]:
    if s["at"] >= old_book - 0.05: s["at"] = round(s["at"] + WC, 4)
C["words"] = [[b, n, round(t + WC, 4) if t >= old_book - 0.05 else t, round(e + WC, 4) if t >= old_book - 0.05 else e] for b, n, t, e in C["words"]]
C["film_end"] = round(C["film_end"] + WC, 4)
C["cues"]["Sixty"] = round(old_book + 0.75, 4)
C["reserved"] = {"b3b": {"line": "And if you join WashClub? Sixty-nine.", "first_word_at": round(old_book + 0.2, 4), "cue_word": "Sixty"}}
C["no_vo"] = ["Sixty"]
# the pickup line, once generated and transcribed (tools/gen-audio.sh pickup, tools/stt_words.sh): B3B=b3b_t1 python3 -I tools/cues_v3.py
take = os.environ.get("B3B")
if take:
    import re
    d = json.load(open(f"assets/audio/vo/{take}.words.json"))
    ws = [(re.sub(r"[^\w']", "", x["text"]).lower(), x["start"], x["end"]) for x in d["words"] if x.get("type") == "word"]
    off = old_book + 0.2 - ws[0][1]
    six = next(t for wd, t, e in ws if wd.startswith("sixty") or wd == "69")
    assert ws[-1][2] + off <= C["cuts"]["book"] - 0.1, "b3b line runs past the booking cut: lengthen WC"
    C["segments"].append({"beat": 3.5, "file": take, "src_from": round(max(0, ws[0][1] - 0.04), 3), "src_to": round(ws[-1][2] + 0.12, 3), "at": round(max(0, ws[0][1] - 0.04) + off, 3)})
    C["cues"]["Sixty"] = round(math.floor((six + off) * 30 + 1e-6) / 30, 4); C["no_vo"] = []
json.dump(C, open("tools/cues.json", "w"), indent=1)
print({k: round(v * 30) for k, v in C["cues"].items()}, {k: round(v * 30) for k, v in C["cuts"].items()}, round(C["film_end"] * 30), C["timer_stop"])
