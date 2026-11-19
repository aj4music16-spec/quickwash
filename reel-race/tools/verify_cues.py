"""Check a render against tools/cues.json without a speech API: rebuild the VO stem exactly as tools/mix.py places it, find
each cue word's acoustic onset there (10 ms envelope crossing -38 dB, the silence-to-voice edge nearest the cue), and find the
picture events in the rendered MP4 (hard cuts = frames whose mean absolute change from the previous frame is a large spike).
Usage: python3 -I tools/verify_cues.py ../dist/quickwash-race.mp4"""
import json, os, subprocess, sys
import numpy as np
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = json.load(open("tools/cues.json")); FILM = C["film_end"]; SR = 16000
stem = np.zeros(int(FILM * SR) + SR, np.float32)
for p in C["segments"]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{p.get('dir', 'assets/audio/vo')}/{p['file']}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)[int(p["src_from"] * SR):int(p["src_to"] * SR)]; i = int(p["at"] * SR); stem[i:i + len(x)] += x
h = SR // 100; env = np.array([20 * np.log10(np.sqrt((stem[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(stem) - h, h)])
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vf", "scale=108:192", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(np.float32); diff = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
cuts = [i for i in range(1, len(diff)) if diff[i] > 18 and diff[i] > 3 * np.median(diff[max(0, i - 6):i + 6])]
print("hard cuts in the render (frames):", cuts)
for k, t in C["cues"].items():
    vis = round(t * 30)
    if k in C.get("no_vo", []): print(f"{k:9s} (no VO)            visual f{vis}"); continue
    on = np.where((env[1:] > -38) & (env[:-1] <= -38))[0] + 1          # every silence -> voice edge
    j = on[np.argmin(np.abs(on - t * 100))]                             # the one nearest the cue
    print(f"{k:9s} voice onset f{round(j / 100 * 30):3d} ({j / 100:5.2f})  visual f{vis}  diff {vis - round(j / 100 * 30):+d}")
