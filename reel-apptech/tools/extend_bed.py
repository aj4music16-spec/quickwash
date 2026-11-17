"""Lengthen the chosen ElevenLabs bed (bed2, 22.05 s) by repeating a stretch of its steady middle, cut at a matched point.
Usage: python3 -I tools/extend_bed.py in.mp3 out.wav repeat_seconds
(bed2 is 116 BPM: one beat 0.5175 s, a bar 2.07 s; repeat two bars, 4.14 s, so the phrasing stays in 4/4)
Search: for a cut at t1 in 10-14 s, jump back to t2 = t1 - L with L within 30 ms of the requested repeat; score = correlation of the
10 ms RMS envelope over the 3 s after each point (beat phase) + correlation of the raw waveform over 40 ms (sample match),
refined to the sample. The two halves are joined with a 40 ms equal-power crossfade."""
import subprocess, sys
import numpy as np
SR = 44100
src, dst, add = sys.argv[1], sys.argv[2], float(sys.argv[3])
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy(); m = x.mean(1)
hop = SR // 100; env = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, "same"))[::hop]
def ecorr(a, b, n=300):
    A, B = env[a:a + n], env[b:b + n]; A = A - A.mean(); B = B - B.mean(); return float((A * B).sum() / (np.linalg.norm(A) * np.linalg.norm(B) + 1e-9))
best = None
for t1 in np.arange(10.0, 14.0, 0.01):
    for L in np.arange(add - 0.03, add + 0.031, 0.005):
        s = ecorr(int(t1 * 100), int((t1 - L) * 100))
        if best is None or s > best[0]: best = (s, t1, L)
s, t1, L = best
i1 = int(t1 * SR); w = int(0.04 * SR); bestj = None
for d in range(-int(0.012 * SR), int(0.012 * SR)):
    j = int((t1 - L) * SR) + d
    a, b = m[i1:i1 + w], m[j:j + w]; c = float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    if bestj is None or c > bestj[0]: bestj = (c, j)
c, i2 = bestj
fade = int(0.04 * SR); tt = np.linspace(0, np.pi / 2, fade)[:, None]
head, tail = x[:i1], x[i2:]
join = head[-fade:] * np.cos(tt) + tail[:fade] * np.sin(tt)
y = np.concatenate([head[:-fade], join, tail[fade:]])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", dst], input=y.astype(np.float32).tobytes(), check=True)
print(f"cut {t1:.2f} s -> jump back to {i2 / SR:.3f} s (repeat {(i1 - i2) / SR:.3f} s); envelope r {s:.3f}, waveform r {c:.3f}; length {len(y) / SR:.2f} s")
