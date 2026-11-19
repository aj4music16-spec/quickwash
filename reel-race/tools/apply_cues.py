"""Write the frame-snapped cue times from tools/cues.json into index.html and the compositions, so the picture always
matches the placed VO.  Usage: python3 -I tools/apply_cues.py  (after tools/vo_plan.py; then re-run check)"""
import json, os, re
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = json.load(open("tools/cues.json"))
f = lambda t: round(t * 30)                                   # frame of a film time
q = {k: f(v) for k, v in C["cues"].items()}; k = {n: f(v) for n, v in C["cuts"].items()}; END = f(C["film_end"])
import math
# seconds string from frames, floored to 0.1 ms: a start must never round to after its frame's time (that delays the cut a frame)
s = lambda fr: f"{math.floor(fr / 30 * 1e4 + 1e-9) / 1e4:.4f}".rstrip("0").rstrip(".")
# durations of back-to-back pieces run 2 ms long: start strings are rounded to 0.1 ms, so start + duration could otherwise end
# a hair before the next piece's start and leave one empty (black) frame at the cut; the later piece paints on top
d = lambda fr: f"{fr / 30 + 0.002:.4f}".rstrip("0").rstrip(".")
def attr(txt, el_id, start=None, dur=None):
    def rep(m):
        t = m.group(0)
        if start is not None: t = re.sub(r'data-start="[^"]*"', f'data-start="{start}"', t)
        if dur is not None: t = re.sub(r'data-duration="[^"]*"', f'data-duration="{dur}"', t)
        return t
    new, n = re.subn(rf'<[a-z]+ id="{el_id}"[^>]*>', rep, txt); assert n == 1, el_id; return new
def const(txt, pattern, value):
    new, n = re.subn(pattern, lambda m: m.group(1) + value + m.group(2), txt); assert n >= 1, pattern; return new
def patch(path, fn):
    t = open(path).read(); t2 = fn(t)
    if t2 != t: open(path, "w").write(t2)

def index(t):
    t = attr(t, "root", 0, s(END)); t = attr(t, "mix", 0, s(END))
    t = attr(t, "hook", 0, d(k["race"])); t = attr(t, "race", s(k["race"]), d(k["payoff"] - k["race"]))
    t = attr(t, "payoff", s(k["payoff"]), d(k["washclub"] - k["payoff"])); t = attr(t, "checklist", s(k["race"]), d(k["washclub"] - k["race"]))
    t = attr(t, "washclub", s(k["washclub"]), d(k["book"] - k["washclub"]))
    t = attr(t, "timer", 0, d(k["washclub"])); t = attr(t, "book", s(k["book"]), d(k["end"] - k["book"])); t = attr(t, "end", s(k["end"]), s(END - k["end"]))
    return t
def hook(t):
    for i in ("hk-v", "hk-h"): t = attr(t, i, 0, d(k["race"]))
    return const(t, r'(repeat: 1, transformOrigin: "0% 50%" \}, )[0-9.]+(\);)', s(q["Go"]))
def race(t):
    ids = ["rc-s1a", "rc-s1b", "rc-s2", "rc-s3", "rc-s4a", "rc-s4b", "rc-s5", "rc-s6"]
    cuts = [q[w] for w in ("Foam", "hand", "Vacuum", "Glass", "Tire", "door", "Interior", "Ceramic")] + [k["payoff"]]
    for i, el in enumerate(ids): t = attr(t, el, s(cuts[i] - k["race"]), d(cuts[i + 1] - cuts[i]))
    return t
def checklist(t):
    t = attr(t, "ck-clip", 0, d(k["washclub"] - k["race"]))
    rows = ", ".join(s(q[w] - k["race"]) for w in ("Foam", "Vacuum", "Glass", "Tire", "Interior", "Ceramic"))
    t = const(t, r"(ROW = \[)[^\]]*(\])", rows); return const(t, r"(PAYOFF = )[0-9.]+(;)", s(k["payoff"] - k["race"]))
def timer(t):
    t = attr(t, "tm-pill", 0, d(k["washclub"]))
    t = const(t, r"(const GO = )[0-9.]+(,)", s(q["Go"])); return const(t, r"(DONE = )[0-9.]+(, el)", s(q["Done"]))
def payoff(t):
    d_ = d(k["washclub"] - k["payoff"])
    for i in ("pay-s9", "pay-price", "pay-line"): t = attr(t, i, 0, d_)
    t = const(t, r'(\{ scale: 1.04, duration: )[0-9.]+(, ease: "power2.out" \}, 0\);)', d_)
    return const(t, r"(const DONE = )[0-9.]+(;)", s(q["Done"] - k["payoff"]))
def washclub(t):
    d_ = d(k["book"] - k["washclub"])
    for i in ("wc-bg", "wc-old", "wc-new", "wc-badge", "wc-small"): t = attr(t, i, 0, d_)
    return const(t, r"(const SIXTY = )[0-9.]+(,)", s(q["Sixty"] - k["washclub"]))
def book(t):
    d_ = d(k["end"] - k["book"])
    for i in ("bk-bg", "bk-dev", "bk-h"): t = attr(t, i, 0, d_)
    t = const(t, r"(const BOOKING = )[0-9.]+(,)", s(q["Booking"] - k["book"])); return const(t, r"(TWENTY = )[0-9.]+(;)", s(q["Twenty"] - k["book"]))
def end(t):
    e = s(END - k["end"])
    for i in ("en-bgclip", "en-ringclip", "en-logoclip", "en-h", "en-dl", "en-badges"): t = attr(t, i, 0, e)
    t = const(t, r'(ease: "back.out\(1.6\)" \}, )[0-9.]+(\);)', s(q["Quick"] - k["end"]))
    t = const(t, r'(ease: "expo.out" \}, )[0-9.]+(\);\n      tl.fromTo\(\["#en-ios")', s(q["Grab"] - k["end"] - 9))
    return const(t, r'(stagger: 0.08 \}, )[0-9.]+(\);)', s(q["Grab"] - k["end"]))
for p, fn in [("index.html", index), ("compositions/hook.html", hook), ("compositions/race.html", race), ("compositions/checklist.html", checklist),
              ("compositions/timer.html", timer), ("compositions/payoff.html", payoff), ("compositions/washclub.html", washclub), ("compositions/book.html", book), ("compositions/end.html", end)]:
    patch(p, fn)
print("frames", q, k, "end", END, "timer stops", (q["Done"] - q["Go"]) / 30)
