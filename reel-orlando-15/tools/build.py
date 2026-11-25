"""15 s cut: write index.html and compositions/*.html from tools/cues.json (the beat-grid cue sheet made by tools/vo_plan.py), so every
cut, checklist row and line sits on its frame.  Usage: python3 -I tools/build.py   (then: npx hyperframes check)
Edit copy and styling here, not in the generated HTML."""
import json, math, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = json.load(open("tools/cues.json")); cut = C["cuts"]; q = C["cues"]; END = C["film_end"]
fr = lambda t: round(t * 30)
s = lambda t: f"{math.floor(fr(t) / 30 * 1e4 + 1e-9) / 1e4:.4f}".rstrip("0").rstrip(".")     # a start never rounds late
d = lambda a, b: f"{(fr(b) - fr(a)) / 30 + 0.002:.4f}".rstrip("0").rstrip(".")              # back-to-back pieces overlap 2 ms
cut["s01"] = 0.0
WIPE_UNDER = 0.4                                     # the price shot runs on under the end-card wipe
ORDER = ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "end"]
FILE = {"s01": "o1-grille-van", "s02": "s05-mitt-rocker", "s03": "s06-inside-door", "s04": "s07-mitt-window", "s05": "s09-door-jamb",
        "s06": "i1-open-door", "s07": "s11-spray-wax", "s08": "s13-hero-front"}
MSTART = {"s01": 0.3, "s05": 0.3}                    # o1 starts at IMG_6406 7.9 s; the jamb shot at IMG_6402 10.9 s (door opens 0.35 s in)
SOUND = {"s05": 0.10}
NOTE = {"s01": "detailer mitt-washing the grille, QuickWash van behind (IMG_6406, plate tracked + blurred)",
        "s02": "hand wash: green mitt on the lower door, wash buckets, open van behind (IMG_0012_1_22)",
        "s03": "vacuum stand-in: detailer (QuickWash hoodie) working inside the open driver door (IMG_2032)",
        "s04": "glass: mitt on the door and side window (IMG_6408; bucket print blurred)",
        "s05": "tires + jambs: rear door opened, detailer rinses the jamb (IMG_6402)",
        "s06": "interior: driver door open on the clean cabin, steady (IMG_6439)",
        "s07": "spray wax misted along the side (IMG_6392)", "s08": "the finished car's front, slow arc (IMG_6432)"}
nxt = {k: cut[ORDER[i + 1]] for i, k in enumerate(ORDER[:-1])}

HEAD = """<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #000; }
    .shot { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }
    /* legibility without a slab: gentle gradient scrims (divs over the footage) + a soft text shadow */
    .tscrim { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; z-index: 2;
      background: linear-gradient(180deg, rgba(0, 0, 20, 0.55) 0%, rgba(0, 0, 20, 0.38) 55%, rgba(0, 0, 20, 0) 100%); }
    .bscrim { position: absolute; left: 0; top: 780px; width: 1080px; height: 1140px; z-index: 2;
      background: linear-gradient(180deg, rgba(0, 0, 20, 0) 0%, rgba(0, 0, 20, 0.45) 30%, rgba(0, 0, 20, 0.55) 60%, rgba(0, 0, 20, 0.5) 100%); }
    .txt { position: absolute; z-index: 3; font-family: Poppins, sans-serif; color: #ffffff;
      text-shadow: 0 3px 18px rgba(0, 0, 10, 0.55), 0 1px 2px rgba(0, 0, 10, 0.5); }
    .txt span { display: block; white-space: nowrap; }
@CSS@  </style>
  <div id="root" data-composition-id="@ID@" data-width="1080" data-height="1920">
"""
TAIL = """  </div>
  <script>
    (function () {
      const F = (f) => f / 30;
      const tl = gsap.timeline({ paused: true });
@JS@      window.__timelines = window.__timelines || {};
      window.__timelines["@ID@"] = tl;
    })();
  </script>
</template>
"""
def head(css, i): return HEAD.replace("@CSS@", css).replace("@ID@", i)
def tail(js, i): return TAIL.replace("@JS@", js).replace("@ID@", i)
def videos(a, b, t0, extra_end=None):
    out = []; ids = ORDER[ORDER.index(a):ORDER.index(b) + 1]
    for k in ids:
        st = cut[k] - t0; en = (extra_end if (k == b and extra_end) else nxt[k]) - t0
        snd = f'playsinline data-has-audio="true" data-volume="{SOUND[k]}"' if k in SOUND else "muted playsinline"
        out.append(f'    <!-- {k}: {NOTE[k]} -->\n    <video id="{k}" class="clip shot" src="assets/footage/{FILE[k]}.mp4" data-start="{s(st)}" '
                   f'data-duration="{d(st, en)}" data-media-start="{MSTART.get(k, 0)}" data-track-index="0" {snd}></video>')
    return "\n".join(out) + "\n"

PIN = ('<svg viewBox="0 0 34 44" aria-hidden="true"><path d="M17 1C8.2 1 1 8 1 16.8 1 28.5 17 43 17 43s16-14.5 16-26.2C33 8 25.8 1 17 1z" '
       'fill="#ffffff" /><circle cx="17" cy="16.5" r="6" fill="#ff6600" /></svg>')
files = {}
# ---- open
t0, t1 = 0.0, cut["s02"]; L = t1 - t0
files["open"] = head("""    #op-chip { position: absolute; left: 72px; top: 200px; height: 72px; padding: 0 28px 0 20px; z-index: 3; display: flex; align-items: center; gap: 12px;
      border-radius: 20px; background: var(--accent, #ff6600); color: #ffffff; font-family: Poppins, sans-serif; font-weight: 700; font-size: 42px;
      line-height: 1; letter-spacing: -0.01em; white-space: nowrap; }
    #op-chip svg { width: 32px; height: 42px; display: block; flex: none; }
    #op-h { left: 72px; top: 300px; width: 860px; font-weight: 700; font-size: 104px; line-height: 1.04; letter-spacing: -0.025em; }
    #op-h2 { left: 72px; top: 540px; width: 860px; font-weight: 600; font-size: 66px; line-height: 1.12; letter-spacing: -0.015em; opacity: 0; }
""", "open") + videos("s01", "s01", t0) + f"""    <div id="op-scrim" class="tscrim" data-layout-ignore></div>
    <!-- frame 0 (the thumbnail): the Orlando chip and the offer are already on screen -->
    <div id="op-chip" class="clip" data-start="0" data-duration="{d(0, L)}" data-track-index="1">{PIN}<span>Orlando, FL</span></div>
    <div id="op-h" class="clip txt" data-start="0" data-duration="{d(0, L)}" data-track-index="2"><span>The $99</span><span>QuickWash.</span></div>
    <div id="op-h2" class="clip txt" data-start="0" data-duration="{d(0, L)}" data-track-index="3"><span>We come to you.</span></div>
""" + tail(f"""      // "We come to you." lands on "We" (film {q['We']:.3f})
      tl.set("#op-h2", {{ opacity: 1 }}, {s(q['We'])});
      tl.fromTo("#op-h2", {{ y: 24 }}, {{ y: 0, duration: F(5), ease: "power4.out" }}, {s(q['We'])});
""", "open")
# ---- service (footage only; the checklist is its own layer)
t0, t1 = cut["s02"], cut["s08"]
files["service"] = head("", "service") + videos("s02", "s07", t0) + '    <div id="sv-scrim" class="bscrim" data-layout-ignore></div>\n' + tail("", "service")
# ---- price
t0, t1 = cut["s08"], cut["end"]; L = t1 - t0; P = 0.0
files["price"] = head("""    #pr-price { left: 64px; top: 300px; color: var(--accent, #ff6600); font-weight: 800; font-size: 250px; line-height: 1; letter-spacing: -0.04em;
      text-shadow: 0 6px 30px rgba(0, 0, 10, 0.45); opacity: 0; }
    #pr-tscrim { background: linear-gradient(180deg, rgba(0, 0, 20, 0.68) 0%, rgba(0, 0, 20, 0.55) 55%, rgba(0, 0, 20, 0) 100%); }   /* bright wall behind the $99 */
    #pr-small { left: 76px; top: 570px; font-weight: 600; font-size: 54px; line-height: 1.1; letter-spacing: -0.01em; opacity: 0; }
""", "price") + videos("s08", "s08", t0, cut["end"] + WIPE_UNDER) + f"""    <div id="pr-tscrim" class="tscrim" data-layout-ignore></div>
    <div id="pr-bscrim" class="bscrim" data-layout-ignore></div>
    <div id="pr-price" class="clip txt" data-start="0" data-duration="{d(0, L)}" data-track-index="1">$99</div>
    <div id="pr-small" class="clip txt" data-start="0" data-duration="{d(0, L)}" data-track-index="2"><span>Standard-size vehicle</span></div>
""" + tail(f"""      // "Ninety-nine" = the cut to the finished car (local {P:.3f}) -> "$99" lands; the size line follows 4 frames later
      tl.set("#pr-price", {{ opacity: 1 }}, {s(P)});
      tl.fromTo("#pr-price", {{ scale: 1.25, transformOrigin: "0% 60%" }}, {{ scale: 1, duration: 0.3, ease: "expo.out" }}, {s(P)});
      tl.set("#pr-small", {{ opacity: 1 }}, {s(P + 4 / 30)});
      tl.fromTo("#pr-small", {{ y: 20 }}, {{ y: 0, duration: F(5), ease: "power4.out" }}, {s(P + 4 / 30)});
""", "price")
# ---- checklist (rows land on the first word of each line; all rows back to full on "All")
t0, t1 = cut["s02"], cut["end"]
ROWS = [("Hand", "Foam + hand wash"), ("Vacuum", "Vacuum: seats, floors, trunk"), ("Glass", "Glass, in + out"),
        ("Tires", "Tire shine + door jambs"), ("Interior", "Interior wiped down"), ("Spray", "Ceramic spray wax")]
rows = "\n".join(f'      <div id="ck-r{i + 1}" class="ck-row" style="top: {890 + 70 * i}px"><div class="ck-badge"><svg viewBox="0 0 24 24"><path d="M7 12.5l3.5 3.5 6.5-7" /></svg></div><div class="ck-label">{lab}</div></div>'
                 for i, (w, lab) in enumerate(ROWS))
files["checklist"] = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #ck-clip {{ position: absolute; inset: 0; }}
    /* as reel-race: six fixed rows, left x 72, pitch 70 px, block y 890-1300, on the shots' bottom scrim, no slab */
    .ck-row {{ position: absolute; left: 72px; height: 60px; display: flex; align-items: center; gap: 18px; opacity: 0; }}
    .ck-badge {{ width: 48px; height: 48px; flex: none; border-radius: 50%; background: var(--accent, #ff6600); }}
    .ck-badge svg {{ width: 48px; height: 48px; display: block; }}
    .ck-badge path {{ fill: none; stroke: #ffffff; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 15; stroke-dashoffset: 15; }}
    .ck-label {{ font-family: Poppins, sans-serif; font-weight: 600; font-size: 50px; line-height: 60px; letter-spacing: -0.01em; color: #ffffff;
      white-space: nowrap; max-width: 800px; text-shadow: 0 3px 18px rgba(0, 0, 10, 0.55), 0 1px 2px rgba(0, 0, 10, 0.5); }}
  </style>
  <div id="root" data-composition-id="checklist" data-width="1080" data-height="1920">
    <div id="ck-clip" class="clip" data-start="0" data-duration="{d(t0, t1)}" data-layout-allow-overflow>
{rows}
    </div>
  </div>
  <script>
    (function () {{
      // row N lands with its section's cut (= the first word of its line, +-2 f) (local = film - {t0:.3f})
      const F = (f) => f / 30, ROW = [{", ".join(s(cut[c] - t0) for c in ("s02", "s03", "s04", "s05", "s06", "s07"))}], ALL = {s(cut["s08"] - t0)};
      const tl = gsap.timeline({{ paused: true }});
      ROW.forEach((t, i) => {{
        const n = i + 1, r = `#ck-r${{n}}`;
        tl.set(r, {{ opacity: 1 }}, t);
        tl.fromTo(`${{r}} .ck-label`, {{ y: 20 }}, {{ y: 0, duration: F(5), ease: "power4.out" }}, t);
        tl.fromTo(`${{r}} .ck-badge`, {{ scale: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: F(6), ease: "back.out(1.7)" }}, t);
        tl.fromTo(`${{r}} path`, {{ strokeDashoffset: 15 }}, {{ strokeDashoffset: 0, duration: F(5), ease: "power2.out" }}, t + F(6));
        if (n > 1) tl.fromTo(`#ck-r${{n - 1}}`, {{ opacity: 1 }}, {{ opacity: 0.78, duration: F(4), ease: "power1.out", immediateRender: false }}, t);
      }});
      tl.fromTo("#ck-r1, #ck-r2, #ck-r3, #ck-r4, #ck-r5", {{ opacity: 0.78 }}, {{ opacity: 1, duration: F(4), ease: "power1.out", immediateRender: false }}, ALL);
      window.__timelines = window.__timelines || {{}};
      window.__timelines["checklist"] = tl;
    }})();
  </script>
</template>
"""
# ---- end card
L = END - cut["end"]
files["end"] = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #end-clip {{ position: absolute; inset: 0; }}
    /* the client's lead-form card (Davenport design, pill repainted ORLANDO, FLORIDA by tools/endcard_pill.py); wipes up, then holds */
    #end-wipe {{ position: absolute; inset: 0; clip-path: inset(100% 0 0 0); background: #000099; }}
    #end-img {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; display: block; }}
  </style>
  <div id="root" data-composition-id="end" data-width="1080" data-height="1920">
    <div id="end-clip" class="clip" data-start="0" data-duration="{d(0, L)}" data-layout-allow-overflow data-layout-ignore>
      <div id="end-wipe"><img id="end-img" src="assets/app/endcard-orlando.jpg" alt="QuickWash, Orlando, Florida. Clean car. Zero hassle. We come to you. $99 QuickWash, standard-size vehicle. Get My $99 QuickWash. Fill out the form below to get started." /></div>
    </div>
  </div>
  <script>
    (function () {{
      // starts on "Drop" (film {cut['end']:.3f}): wipe up in 12 frames (as reel-glendale), then still
      const F = (f) => f / 30;
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#end-wipe", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: F(12), ease: "power3.inOut" }}, 0);
      window.__timelines = window.__timelines || {{}};
      window.__timelines["end"] = tl;
    }})();
  </script>
</template>
"""
for k, v in files.items(): open(f"compositions/{k}.html", "w").write(v)

host = lambda i, a, b, z, kind="graphics", tr=1: (f'      <div id="{i}" data-composition-id="{i}" data-composition-src="compositions/{i}.html" data-start="{s(a)}" '
                                                 f'data-duration="{d(a, b)}"\n        data-track-index="{tr}" data-track-kind="{kind}" data-width="1080" data-height="1920" style="z-index: {z}"></div>')
index = f"""<!doctype html>
<html
  lang="en"
  data-composition-variables='[
    {{"id":"navy","type":"color","label":"Brand navy","default":"#000099"}},
    {{"id":"accent","type":"color","label":"Brand orange","default":"#ff6600"}}
  ]'
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: Poppins, sans-serif; }}
      #stage {{ position: absolute; inset: 0; background: #000; }}
    </style>
  </head>
  <body>
    <!-- "The $99 QuickWash, Orlando", 15 s cut (Meta lead form). 1080x1920, 30 fps, {fr(END)} frames. Cuts on the bed's 110 BPM beat grid; each
         section's line starts on its first cut (tools/vo_plan.py -> tools/cues.json -> tools/build.py). -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{s(END)}" data-width="1080" data-height="1920">
      <div id="stage" data-layout-ignore></div>
      <!-- 1. OPEN: detailer at the QuickWash van; chip + offer on frame 0 -->
{host("open", 0, cut["s02"], 1)}
      <!-- 2. THE SERVICE: six shots, one per inclusion -->
{host("service", cut["s02"], cut["s08"], 2)}
      <!-- 3. PRICE: "$99" on "Ninety-nine" (the shot runs on under the end-card wipe) -->
{host("price", cut["s08"], cut["end"] + WIPE_UNDER, 3)}
      <!-- the package checklist over the service and the price -->
{host("checklist", cut["s02"], cut["end"], 6, tr=2)}
      <!-- 4. END CARD: the Orlando lead-form card wipes up on "Drop" -->
{host("end", cut["end"], END, 7, tr=3)}
      <!-- premix: ElevenLabs acoustic bed + Liam (eleven_v3), ducked, -14 LUFS (tools/mix.py) -->
      <audio id="mix" class="clip" data-start="0" data-duration="{s(END)}" data-track-index="4" data-volume="1" src="assets/audio/mix.m4a"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open("index.html", "w").write(index)
print("wrote index.html +", ", ".join(files), "| end", END, fr(END), "frames")
