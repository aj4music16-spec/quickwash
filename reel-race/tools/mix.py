"""reel-race premix (main cut: Laura, tools/vo_plan_laura.py; the Liam alt used tools/cues-liam.json -> mix-liam.m4a): ElevenLabs bed (bed2, ~128 BPM, two bars repeated by tools/extend_bed.py) + eleven_v3 VO placed from
tools/cues.json + UI sounds: a soft tick on every second of the race timer (Go + 1 s ... until it stops), a ding on "Done",
whooshes into each beat, a tap on "Booking" and a success chime on "Twenty". Music side-chain ducked under the VO;
loudnorm -14 LUFS, limiter, AAC.  (The hook foam and the wheel rinse keep their own clip sound at 0.12 in the video
elements, as in reel-hp.)  Usage: python3 -I tools/mix.py [out.m4a] [cues.json]"""
import json, math, os, subprocess, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
out = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/mix.m4a"
C = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "tools/cues.json")); FILM = C["film_end"]; q = C["cues"]; cuts = C["cuts"]
SFX = [("tick", q["Go"] + n, -2) for n in range(1, math.floor(C["timer_stop"]) + 1)]
SFX += [("ding", q["Done"], -10), ("tap", q["Booking"], -4), ("success", q["Twenty"] + 0.03, -14)]
SFX += [("whoosh", t - 0.05, -18) for t in (cuts["payoff"], cuts["book"], cuts["end"])]
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB"
ins = ["-i", "assets/audio/music/bed2_ext.wav"]; fc = []; vo = []; fx = []; n = 1
for p in C["segments"]:
    ins += ["-i", f"{p.get('dir', 'assets/audio/vo')}/{p['file']}.mp3"]; d = round(p["src_to"] - p["src_from"], 3); ms = int(round(p["at"] * 1000))
    fc.append(f"[{n}]aformat=sample_rates=48000:channel_layouts=stereo,atrim={p['src_from']}:{p['src_to']},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.015,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,adelay={ms}|{ms}[v{n}]"); vo.append(f"[v{n}]"); n += 1
for f, t, g in SFX:
    ins += ["-i", f"assets/audio/sfx/{f}.mp3"]; ms = int(round(t * 1000))
    fc.append(f"[{n}]aformat=sample_rates=48000:channel_layouts=stereo,{TRIM},volume={g}dB,adelay={ms}|{ms}[s{n}]"); fx.append(f"[s{n}]"); n += 1
fc.append(f"{''.join(vo)}amix=inputs={len(vo)}:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,"
          f"apad=whole_dur={FILM},atrim=0:{FILM},asplit=2[vo][sc]")
fc.append(f"{''.join(fx)}amix=inputs={len(fx)}:normalize=0,apad=whole_dur={FILM},atrim=0:{FILM}[fx]")
fc.append(f"[0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{FILM},afade=t=in:d=0.02,afade=t=out:st={FILM - 1.0}:d=1.0,volume=0.45[mus]")
fc.append("[mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=300:makeup=1[duck]")
fc.append(f"[duck][fx][vo]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.7:level=false,atrim=0:{FILM}[out]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", ";\n".join(fc), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", out], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(f"wrote {out}", " | ".join(l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "Peak:"))), f"ticks {len([s for s in SFX if s[0] == 'tick'])}")
