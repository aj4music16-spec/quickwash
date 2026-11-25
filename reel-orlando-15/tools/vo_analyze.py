"""Score eleven_v3 takes: word onsets from the character alignment, duration, and pitch movement.
Usage: python3 -I tools/vo_analyze.py assets/audio/vo3/liam_b2_t1 [...]   (paths without extension)
Pitch: autocorrelation F0 per 40 ms frame (10 ms hop, 70-400 Hz, voiced when the normalised ACF peak > 0.5 and the frame is
within 30 dB of the loudest); reports the 10-90% F0 spread and the F0 standard deviation in semitones (more = less monotone)."""
import json, re, subprocess, sys
import numpy as np

def words(al):
    ch, st = al["characters"], al["character_start_times_seconds"]
    text = "".join(ch); out = []; i = 0
    for m in re.finditer(r"\[[^\]]*\]|[A-Za-z0-9'’]+", text):
        if m.group().startswith("["): continue
        out.append((m.group(), st[m.start()], al["character_end_times_seconds"][m.end() - 1]))
    return out

def f0_stats(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); N, H = 640, 160
    frames = [x[i:i + N] for i in range(0, len(x) - N, H)]
    rms = np.array([np.sqrt((f ** 2).mean()) + 1e-9 for f in frames]); top = rms.max()
    f0 = []
    for f, r in zip(frames, rms):
        if 20 * np.log10(r / top) < -30: continue
        f = f - f.mean(); ac = np.correlate(f, f, "full")[N - 1:]; ac /= ac[0] + 1e-9
        lo, hi = 16000 // 400, 16000 // 70; lag = lo + int(np.argmax(ac[lo:hi]))
        if ac[lag] > 0.5: f0.append(16000 / lag)
    st = 12 * np.log2(np.array(f0) / np.median(f0))
    return len(x) / 16000, np.percentile(st, 90) - np.percentile(st, 10), st.std(), len(f0)

for p in sys.argv[1:]:
    al = json.load(open(p + ".json")); w = words(al)
    dur, spread, sd, n = f0_stats(p + ".mp3")
    print(f"{p.split('/')[-1]:16s} dur {dur:5.2f}  F0 spread {spread:4.1f} st  sd {sd:4.2f}  words {len(w)}  span {w[0][1]:.2f}-{w[-1][2]:.2f}")
    print("   " + "  ".join(f"{t}@{s:.2f}" for t, s, e in w))
