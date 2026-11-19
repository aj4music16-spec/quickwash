#!/usr/bin/env python3
"""Build a ready-to-render HyperFrames project in the timeline-edit-reel style from a small JSON spec.

    python3 -I build_timeline.py path/to/timeline.spec.json [--out DIR] [--skip-media]

The project is written to --out (default: the spec's own folder). Paths inside the spec are relative to
the spec file. Needs ffmpeg/ffprobe on PATH and numpy (for the beat grid, via beats.py next to this file).

It produces:
  assets/footage/<id>.mp4    trimmed, 30 fps, 1080x1920 (cover-cropped), silent
  assets/thumbs/<id>.jpg     filmstrip thumbnails for each clip tile (ffmpeg tile)
  assets/audio/music.m4a     the bed trimmed to start on a beat, loudness-normalised (default -14 LUFS, TP -1.5)
  assets/brand/logo.png      end-card logo (if any)       assets/vendor/gsap.min.js
  compositions/timeline.html the overlay (assets/timeline-overlay.html with the segment list baked in)
  compositions/end.html      the end card (if any)
  index.html, package.json, hyperframes.json, meta.json, timeline.json (resolved schedule)
See SKILL.md for the spec format.
"""
import argparse, json, math, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
CLI = "hyperframes@0.9.27"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("command failed: " + " ".join(cmd) + "\n" + r.stderr[-2000:])
    return r


def probe_dur(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout
    return float(out.strip())


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------- schedule
def schedule(spec, base):
    fps = spec.get("fps", 30)
    snap = lambda t: round(round(t * fps) / fps, 4)
    music = spec.get("music") or {}
    grid = spec.get("grid", {})
    period, t0, beatinfo = None, 0.0, None
    if music.get("file"):
        mpath = os.path.join(base, music["file"])
        bpm = music.get("bpm")
        if not bpm or music.get("start", "auto") == "auto":
            import beats
            beatinfo = beats.analyse(mpath)
        period = 60.0 / bpm if bpm else beatinfo["period"]
        st = music.get("start", "auto")
        if st == "auto":
            # first strong onset after min_start: the film's t=0 lands on it, so every beat k is at k*period
            cand = [o["t"] for o in beatinfo["onsets"] if o["s"] >= music.get("min_strength", 0.6) and o["t"] >= music.get("min_start", 0.5)]
            t0 = cand[0] if cand else beatinfo["phase"]
        else:
            t0 = float(st)
    use_beats = period is not None and spec.get("timing", "beats") == "beats"

    def length(item, key_beats, key_s, default_beats, default_s):
        if use_beats:
            return item.get(key_beats, default_beats) * period
        return item.get(key_s, default_s)

    segs, t, clips = [], 0.0, spec["clips"]
    # boundaries are accumulated in exact time and snapped to frames one by one (no drift)
    for i, c in enumerate(clips):
        cid = c.get("id", f"c{i + 1}")
        d = length(c, "beats", "dur", grid.get("clip_beats", 2), grid.get("clip_s", 1.0))
        segs.append({"id": cid, "kind": "clip", "t0": t, "t1": t + d, "src": c["file"], "in": c.get("in", 0.0),
                     "label": c.get("label"), "note": c.get("note", "")})
        t += d
        if i < len(clips) - 1 or c.get("gap_after_beats") or c.get("gap_after"):
            g = length(c, "gap_after_beats", "gap_after", grid.get("gap_beats", 1), grid.get("gap_s", 0.5))
            if i == len(clips) - 1 and not (c.get("gap_after_beats") or c.get("gap_after")):
                g = 0
            if g > 0:
                segs.append({"id": f"g{i + 1}", "kind": "gap", "t0": t, "t1": t + g, "label": c.get("gap_label")})
                t += g
    footage_end = t
    end = spec.get("end_card")
    if end:
        d = end.get("beats", 4) * period if use_beats else end.get("dur", 2.0)
        segs.append({"id": "end", "kind": "end", "t0": t, "t1": t + d, "label": end.get("label", ""),
                     "labelColor": end.get("label_color", end.get("navy", "#000099")), "tileColor": end.get("tile_color", "#ffffff")})  # the tile is a thumbnail of the (white) end card
        t += d
    for s in segs:
        s["start"], s["end"] = snap(s.pop("t0")), snap(s.pop("t1"))
    total = segs[-1]["end"]
    return {"fps": fps, "segments": segs, "total": total, "footageEnd": snap(footage_end),
            "music": {"period": period, "bpm": round(60 / period, 3) if period else None, "start_in_file": t0,
                      "detected": {k: beatinfo[k] for k in ("bpm", "phase")} if beatinfo else None}}


# ---------------------------------------------------------------- media
def build_media(spec, base, out, sch):
    W, H, fps = spec.get("width", 1080), spec.get("height", 1920), sch["fps"]
    ov = spec.get("overlay", {})
    pxps = ov.get("px_per_s", 372)
    th = 134  # thumbnail height in the strip (panel 154 - 2*10 inset)
    tw = round(th * W / H)
    os.makedirs(f"{out}/assets/footage", exist_ok=True)
    os.makedirs(f"{out}/assets/thumbs", exist_ok=True)
    for s in sch["segments"]:
        if s["kind"] != "clip":
            continue
        src = os.path.join(base, s["src"])
        d = s["end"] - s["start"]
        have = probe_dur(src) - s["in"]
        if have < d - 0.02:
            print(f"warning: {s['id']} needs {d:.2f}s but {s['src']} has {have:.2f}s after in={s['in']}; the last frame will hold")
        dst = f"{out}/assets/footage/{s['id']}.mp4"
        # +3 frames of tail so the clip never runs out on its last frame
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["in"]), "-i", src, "-t", f"{d + 3 / fps:.4f}", "-an",
             "-vf", f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1",
             "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst])
        n = max(1, math.ceil((d * pxps) / tw) + 1)
        run(["ffmpeg", "-v", "error", "-y", "-i", dst, "-vf",
             f"fps={(n + 1) / d:.5f},scale={tw * 2}:{th * 2}:force_original_aspect_ratio=increase,crop={tw * 2}:{th * 2},tile={n}x1",
             "-frames:v", "1", "-q:v", "3", f"{out}/assets/thumbs/{s['id']}.jpg"])
        s["file"] = f"assets/footage/{s['id']}.mp4"
        s["thumb"] = f"assets/thumbs/{s['id']}.jpg"
        print(f"  {s['id']}: {s['src']} in {s['in']} -> {s['start']:.3f}-{s['end']:.3f} ({d:.3f}s), {n} thumbs")

    m = spec.get("music") or {}
    if m.get("file"):
        os.makedirs(f"{out}/assets/audio", exist_ok=True)
        src = os.path.join(base, m["file"])
        T = sch["total"]
        fo = m.get("fade_out", 0.8)
        I, TP = m.get("lufs", -14), m.get("true_peak", -1.5)
        st = sch["music"]["start_in_file"]
        # tiny pre-roll fade-in (8 ms) avoids a click when the bed starts mid-waveform
        chain = f"afade=t=in:d=0.008,afade=t=out:st={T - fo:.3f}:d={fo}"
        r = run(["ffmpeg", "-v", "info", "-y", "-ss", f"{st:.4f}", "-i", src, "-t", f"{T:.4f}", "-af",
                 chain + f",loudnorm=I={I}:TP={TP}:LRA=11:print_format=json", "-f", "null", "-"])
        js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
        ln = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
              f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{st:.4f}", "-i", src, "-t", f"{T:.4f}", "-af",
             chain + "," + ln + ",aresample=48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k", f"{out}/assets/audio/music.m4a"])
        r = run(["ffmpeg", "-v", "info", "-i", f"{out}/assets/audio/music.m4a", "-af", "ebur128=peak=true", "-f", "null", "-"])
        tail = r.stderr[r.stderr.rfind("Summary:"):]
        I_ = re.search(r"I:\s+(-?[\d.]+) LUFS", tail); P_ = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
        sch["music"]["lufs"] = float(I_.group(1)) if I_ else None
        sch["music"]["true_peak"] = float(P_.group(1)) if P_ else None
        print(f"  music: {m['file']} from {st:.3f}s, {T:.3f}s, {sch['music']['lufs']} LUFS, TP {sch['music']['true_peak']} dBTP")


# ---------------------------------------------------------------- html
END_HTML = """<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #ffffff; font-family: Poppins, sans-serif; }}
    #ec-bg {{ position: absolute; inset: 0;
      background-image: radial-gradient(circle at 50% 46%, {navy_a} 0%, rgba(0, 0, 0, 0) 38%),
        linear-gradient({navy_b} 1px, transparent 1px), linear-gradient(90deg, {navy_b} 1px, transparent 1px);
      background-size: 100% 100%, 60px 60px, 60px 60px; background-position: 0 0, 30px 30px, 30px 30px; }}
    #ec-logo {{ position: absolute; left: 330px; top: 620px; width: 420px; height: 420px; }}
    #ec-logo img {{ width: 420px; height: 420px; display: block; }}
    #ec-h {{ position: absolute; left: 60px; width: 960px; top: 1070px; text-align: center; color: {navy}; font-weight: 700;
      font-size: 76px; line-height: 1.08; letter-spacing: -0.03em; }}
    #ec-h span {{ display: block; white-space: nowrap; }}
    #ec-h em {{ font-style: normal; color: {accent_text}; }}
    #ec-sub {{ position: absolute; left: 0; width: 1080px; top: 1262px; text-align: center; color: {accent_text}; font-weight: 700;
      font-size: 34px; letter-spacing: 0.12em; text-transform: uppercase; }}
  </style>
  <div id="root" data-composition-id="end" data-width="1080" data-height="1920">
    <div id="ec-bgclip" class="clip" data-start="0" data-duration="{dur}" data-track-index="0" style="position: absolute; inset: 0" data-layout-ignore><div id="ec-bg"></div></div>
    <div id="ec-logoclip" class="clip" data-start="0" data-duration="{dur}" data-track-index="1" style="position: absolute; inset: 0" data-layout-ignore>
      <div id="ec-logo"><img src="assets/brand/logo.png" alt="{brand}" /></div>
    </div>
    <div id="ec-h" class="clip" data-start="0" data-duration="{dur}" data-track-index="2">{line_html}</div>
    <div id="ec-sub" class="clip" data-start="0" data-duration="{dur}" data-track-index="3">{sub}</div>
  </div>
  <script>
    (function () {{
      // the card hard-cuts in on the beat (like every cut in the reel); only its contents move, briefly
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#ec-logo", {{ scale: 0.86, opacity: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "expo.out" }}, 0);
      tl.fromTo("#ec-h > span", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "expo.out", stagger: 0.06 }}, 0.06);
      tl.fromTo("#ec-sub", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, {sub_at});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["end"] = tl;
    }})();
  </script>
</template>
"""


def hexa(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {a})"


def write_project(spec, base, out, sch):
    W, H, fps = spec.get("width", 1080), spec.get("height", 1920), sch["fps"]
    ov = spec.get("overlay", {})
    T = sch["total"]
    segs = sch["segments"]
    os.makedirs(f"{out}/compositions", exist_ok=True)
    os.makedirs(f"{out}/assets/vendor", exist_ok=True)
    shutil.copy(f"{SKILL}/assets/gsap.min.js", f"{out}/assets/vendor/gsap.min.js")

    # overlay: bake the segment list into the template
    ospec = {"decimal": spec.get("decimal", "."), "pxPerSecond": ov.get("px_per_s", 372), "total": T,
             "footageEnd": sch["footageEnd"],
             "segments": [{k: s[k] for k in ("id", "kind", "start", "end", "label", "labelColor", "tileColor", "thumb") if k in s}
                          for s in segs]}
    end = spec.get("end_card")
    if end and end.get("logo"):
        os.makedirs(f"{out}/assets/brand", exist_ok=True)
        shutil.copy(os.path.join(base, end["logo"]), f"{out}/assets/brand/logo.png")
        for s in ospec["segments"]:
            if s["kind"] == "end":
                s["thumb"] = "assets/brand/logo.png"
    html = open(f"{SKILL}/assets/timeline-overlay.html").read()
    html = re.sub(r"/\*SPEC\*/.*?/\*ENDSPEC\*/", "/*SPEC*/ " + json.dumps(ospec, indent=1).replace("\n", "\n        ") + " /*ENDSPEC*/", html, flags=re.S)
    html = re.sub(r'(data-tl-span="all" data-duration=")[^"]*', rf"\g<1>{T}", html)
    html = re.sub(r'(data-tl-span="footage" data-duration=")[^"]*', rf"\g<1>{sch['footageEnd']}", html)
    html = re.sub(r"^<!--.*?-->\n", "", html, flags=re.S)
    open(f"{out}/compositions/timeline.html", "w").write(html)

    hosts = []
    if end:
        es = [s for s in segs if s["kind"] == "end"][0]
        ed = round(es["end"] - es["start"], 4)
        lines = end.get("line", "").split("|")
        def em(txt):
            w = end.get("accent_word")
            return esc(txt).replace(esc(w), f"<em>{esc(w)}</em>") if w else esc(txt)
        line_html = "".join(f"<span>{em(l.strip())}</span>" for l in lines)
        open(f"{out}/compositions/end.html", "w").write(END_HTML.format(
            dur=ed, navy=end.get("navy", "#000099"),
            # brand orange #FF6600 on white is 2.9:1; text uses a slightly deeper orange (>= 3:1) unless told otherwise
            accent_text=end.get("accent_text", "#E85D00"),
            navy_a=hexa(end.get("navy", "#000099"), 0.08), navy_b=hexa(end.get("navy", "#000099"), 0.045),
            brand=esc(end.get("brand", "")), line_html=line_html, sub=esc(end.get("sub", "")), sub_at=end.get("sub_at", 0.5)))
        hosts.append(f'      <div id="end" data-composition-id="end" data-composition-src="compositions/end.html" data-start="{es["start"]}" '
                     f'data-duration="{ed}"\n        data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 5"></div>')

    vids = []
    for s in segs:
        if s["kind"] != "clip":
            continue
        d = round(s["end"] - s["start"], 4)
        note = f"      <!-- {s['id']}: {esc(s.get('note') or s['src'])} -->\n"
        vids.append(note + f'      <video id="v-{s["id"]}" class="clip shot" src="{s["file"]}" data-start="{s["start"]}" data-duration="{d}" '
                    f'data-media-start="0" data-track-index="0" muted playsinline></video>')
    sched = " | ".join(f"{s['id']} {s['start']:.3f}-{s['end']:.3f}" for s in segs)
    audio = ""
    if (spec.get("music") or {}).get("file"):
        audio = (f'      <!-- music: {esc(spec["music"]["file"])} from {sch["music"]["start_in_file"]:.3f}s (a beat), '
                 f'{sch["music"]["lufs"]} LUFS / {sch["music"]["true_peak"]} dBTP (build_timeline.py) -->\n'
                 f'      <audio id="music" class="clip" data-start="0" data-duration="{T}" data-track-index="3" data-volume="1" src="assets/audio/music.m4a"></audio>')
    idx = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: Inter, sans-serif; }}
      #stage {{ position: absolute; inset: 0; background: #000; }}
      .shot {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; z-index: 1; }}
    </style>
  </head>
  <body>
    <!-- {esc(spec.get("title", "timeline-edit reel"))}: built by .claude/skills/timeline-edit-reel/scripts/build_timeline.py from {esc(os.path.basename(spec.get("_spec_path", "timeline.spec.json")))}.
         {W}x{H}, {fps} fps, {T:.3f} s ({round(T * fps)} frames). Footage clips separated by black beats; the editor-timeline overlay on top.
         schedule: {sched} -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="{W}" data-height="{H}">
      <div id="stage" data-layout-ignore></div>
{chr(10).join(vids)}
{chr(10).join(hosts)}
      <!-- the editor timeline: label, scrolling filmstrip, handles, "+", fixed playhead (same segment list as the clips above) -->
      <div id="timeline" data-composition-id="timeline" data-composition-src="compositions/timeline.html" data-start="0" data-duration="{T}"
        data-track-index="2" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 10"></div>
{audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    open(f"{out}/index.html", "w").write(idx)
    name = os.path.basename(os.path.abspath(out))
    pkg = {"name": name, "private": True, "type": "module", "scripts": {
        "dev": f"npx --yes {CLI} preview", "check": f"npx --yes {CLI} check", "render": f"npx --yes {CLI} render",
        "publish": f"npx --yes {CLI} publish"}}
    json.dump(pkg, open(f"{out}/package.json", "w"), indent=2)
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}, "authoringSkill": "hyperframes"}, open(f"{out}/hyperframes.json", "w"), indent=2)
    if not os.path.exists(f"{out}/meta.json"):
        json.dump({"id": name, "name": name}, open(f"{out}/meta.json", "w"), indent=2)
    json.dump(sch, open(f"{out}/timeline.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    ap.add_argument("--skip-media", action="store_true", help="only rewrite the HTML (media already built)")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.spec))
    spec = json.load(open(a.spec))
    spec["_spec_path"] = a.spec
    out = os.path.abspath(a.out or base)
    sch = schedule(spec, base)
    if a.skip_media:
        old = json.load(open(f"{out}/timeline.json"))
        for s in sch["segments"]:
            if s["kind"] == "clip":
                s["file"], s["thumb"] = f"assets/footage/{s['id']}.mp4", f"assets/thumbs/{s['id']}.jpg"
        sch["music"].update({k: old["music"].get(k) for k in ("lufs", "true_peak")})
    else:
        build_media(spec, base, out, sch)
    write_project(spec, base, out, sch)
    m = sch["music"]
    print(f"built {out}: {sch['total']:.3f}s = {round(sch['total'] * sch['fps'])} frames"
          + (f", {m['bpm']} BPM, beat {m['period']:.4f}s" if m["period"] else ""))
    for s in sch["segments"]:
        print(f"  {s['kind']:4} {s['id']:4} {s['start']:7.3f} -> {s['end']:7.3f}  ({s['end'] - s['start']:.3f}s)  {s.get('label') or ''}")


if __name__ == "__main__":
    main()
