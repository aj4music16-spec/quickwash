"""Premix for the Orlando ad: ElevenLabs acoustic bed (bed1, shortened to 15.4 s by tools/shorten_bed.py (its own ending kept)) + Liam's VO placed from
tools/cues.json. VO: high-pass + gentle compressor; bed at 0.5, side-chain ducked under the VO; loudnorm -14 LUFS / TP -2,
4x-oversampled limiter. (Clip sound on a few shots stays on their <video> elements at 0.10-0.12.)
Usage: python3 -I tools/mix.py [out.m4a]"""
import json, os, subprocess, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
out = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/mix.m4a"
C = json.load(open("tools/cues.json")); FILM = C["film_end"]
ins = ["-i", "assets/audio/music/bed1_15.wav"]; fc = []; vo = []
for n, p in enumerate(C["segments"], 1):
    ins += ["-i", f"assets/audio/vo/{p['file']}.mp3"]; dd = round(p["src_to"] - p["src_from"], 3); ms = int(round(p["at"] * 1000))
    fc.append(f"[{n}]aformat=sample_rates=48000:channel_layouts=stereo,atrim={p['src_from']}:{p['src_to']},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.015,afade=t=out:st={max(0, dd - 0.03):.3f}:d=0.03,adelay={ms}|{ms}[v{n}]"); vo.append(f"[v{n}]")
fc.append(f"{''.join(vo)}amix=inputs={len(vo)}:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,"
          f"apad=whole_dur={FILM},atrim=0:{FILM},asplit=2[vo][sc]")
fc.append(f"[0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{FILM},afade=t=in:d=0.02,volume=0.5[mus]")
fc.append("[mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=300:makeup=1[duck]")
fc.append(f"[duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,aresample=192000,alimiter=limit=0.7:level=false,aresample=48000,atrim=0:{FILM}[out]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", ";\n".join(fc), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", out], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(f"wrote {out}", " | ".join(l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "Peak:"))))
