"""Mix voiceover, music and effects onto rendered frames. Timing follows config.json, so adding or
reordering a scene needs no changes here.

usage: python3 tools/mix.py <frames_dir> <out.mp4>   (run from the reel folder)
"""
import json, subprocess, sys

FR, OUT = sys.argv[1], sys.argv[2]
cfg = json.load(open("config.json")); A = "assets/audio"
vo, sfx, t = [], [], 0.0
for i, sc in enumerate(cfg["scenes"]):
    vo.append((sc["vo"], t + 0.4))
    if i:
        sfx.append(("whoosh", max(0, t - 0.05), 0.55))
    sfx.append(("pop", t + 0.5, 0.4))
    if sc["name"] == "reset":
        sfx.append(("splash", t + 0.15, 0.5))
    if sc["name"] in ("effect", "better"):
        sfx.append(("sparkle", t + 0.55, 0.4))
    if sc["name"] == "fresh":
        sfx.append(("pop", t + 1.9, 0.5))
    t += sc["dur"]
dur = t
args = ["-framerate", str(cfg["fps"]), "-i", f"{FR}/f%05d.jpg", "-i", f"{A}/music.mp3"]
fc = f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume=0.7,afade=t=in:d=0.1,afade=t=out:st={dur-1.0}:d=1.0[bed];"
i, lab = 2, ""
for name, at, g in sfx:
    args += ["-i", f"{A}/{name}.wav"]; ms = int(at * 1000)
    fc += f"[{i}:a]aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[s{i}];"; lab += f"[s{i}]"; i += 1
fc += f"{lab}amix=inputs={len(sfx)}:normalize=0:duration=longest,apad=whole_dur={dur},volume=1.3,asplit[sfx][sc];"
vl = ""
for name, at in vo:
    args += ["-i", f"{A}/vo/{name}.wav"]; ms = int(at * 1000)
    fc += f"[{i}:a]aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}];"; vl += f"[v{i}]"; i += 1
fc += (f"{vl}amix=inputs={len(vo)}:normalize=0:duration=longest,apad=whole_dur={dur},highpass=f=80,"
       "acompressor=threshold=0.1:ratio=3:attack=5:release=120,volume=2.2,asplit[vo][vsc];"
       "[bed][sc]sidechaincompress=threshold=0.03:ratio=5:attack=4:release=220[b1];"
       "[b1][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=300[b2];"
       "[b2][sfx][vo]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.7,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k", "-t", str(dur),
                "-movflags", "+faststart", OUT], check=True)
print("mixed", OUT, f"{dur:.2f}s")
