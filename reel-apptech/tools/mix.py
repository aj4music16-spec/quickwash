"""v2 premix: extended ElevenLabs bed (bed2 + two repeated bars, tools/extend_bed.py) + eleven_v3 VO placed phrase by phrase
from tools/cues.json (tools/vo_plan.py) + ElevenLabs UI sounds on the picture's tap/cut times; music side-chain ducked under
the voice; loudnorm -14 LUFS, limiter, AAC.  Usage: python3 -I tools/mix.py liam|jessica [out.m4a]"""
import json, os, subprocess, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); os.chdir(ROOT)
voice = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else f"assets/audio/mix-{voice}.m4a"
C = json.load(open("tools/cues.json")); FILM = C["film_end"]
cue = {c["word"]: c["t"] for c in C["cues"]}
# UI sounds: (file, film time, gain dB). Taps land on the press frame (= the cue word), whooshes lead each cut by 50 ms.
SFX = [("tap", cue["car"], -4), ("tap", cue["wash"], -4), ("tap", cue["time"], -4), ("tap", cue["booked"], -4), ("success", cue["booked"] + 0.04, -14)]
SFX += [("whoosh", t - 0.05, -16) for t in C["beat_starts"][1:]]
SFX += [("whoosh", cue[w] - 0.05, -22) for w in ("office", "gym", "golf")]
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB"
ins = ["-i", "assets/audio/music/bed2_ext.wav"]; fc = []; vo = []; fx = []; n = 1
for p in C["plan"][voice]:
    ins += ["-i", f"assets/audio/vo3/{p['file']}.mp3"]; d = round(p["src_to"] - p["src_from"], 3); ms = int(round(p["at"] * 1000))
    fc.append(f"[{n}]aformat=sample_rates=48000:channel_layouts=stereo,atrim={p['src_from']}:{p['src_to']},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.015,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,adelay={ms}|{ms}[v{n}]"); vo.append(f"[v{n}]"); n += 1
for f, t, g in SFX:
    ins += ["-i", f"assets/audio/sfx/{f}.mp3"]; ms = int(round(t * 1000))
    fc.append(f"[{n}]aformat=sample_rates=48000:channel_layouts=stereo,{TRIM},volume={g}dB,adelay={ms}|{ms}[s{n}]"); fx.append(f"[s{n}]"); n += 1
fc.append(f"{''.join(vo)}amix=inputs={len(vo)}:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,"
          f"apad=whole_dur={FILM},atrim=0:{FILM},asplit=2[vo][sc]")
fc.append(f"{''.join(fx)}amix=inputs={len(fx)}:normalize=0,apad=whole_dur={FILM},atrim=0:{FILM}[fx]")
fc.append(f"[0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{FILM},afade=t=out:st={FILM - 0.9}:d=0.9,volume=0.5[mus]")
fc.append("[mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=350:makeup=1[duck]")
fc.append(f"[duck][fx][vo]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.75:level=false,atrim=0:{FILM}[out]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", ";\n".join(fc), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", out], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = [l for l in r.splitlines() if l.strip().startswith(("I:", "Peak:"))]
print(f"wrote {out}", " | ".join(x.strip() for x in I))
