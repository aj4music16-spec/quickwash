"""Shorten the bed for the 15 s cut: keep its start and its own ending, and skip a stretch in between whose length is a whole number
of bars, so the beat grid before the splice (110 BPM, beat 0 at 0.130 s) stays valid after it and the bed ends on its own final hit.
Usage: python3 -I tools/shorten_bed.py in.mp3 out.wav skip_seconds
Search: splice point t1 in 4-9 s, jump forward to t2 = t1 + L with L within 30 ms of the request; score = correlation of the 10 ms
RMS envelope over the 3 s after each point + raw-waveform correlation over 40 ms, refined to the sample; 40 ms equal-power crossfade."""
import subprocess, sys
import numpy as np
SR = 44100
src, dst, skip = sys.argv[1], sys.argv[2], float(sys.argv[3])
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy(); m = x.mean(1)
hop = SR // 100; env = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, "same"))[::hop]
def ecorr(a, b, n=300):
    A, B = env[a:a + n], env[b:b + n]; A = A - A.mean(); B = B - B.mean(); return float((A * B).sum() / (np.linalg.norm(A) * np.linalg.norm(B) + 1e-9))
best = None
for t1 in np.arange(4.0, 9.0, 0.01):
    for L in np.arange(skip - 0.03, skip + 0.031, 0.005):
        s = ecorr(int(t1 * 100), int((t1 + L) * 100))
        if best is None or s > best[0]: best = (s, t1, L)
s, t1, L = best
i1 = int(t1 * SR); w = int(0.04 * SR); bestj = None
for d in range(-int(0.012 * SR), int(0.012 * SR)):
    j = int((t1 + L) * SR) + d
    a, b = m[i1:i1 + w], m[j:j + w]; c = float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    if bestj is None or c > bestj[0]: bestj = (c, j)
c, i2 = bestj
fade = int(0.04 * SR); tt = np.linspace(0, np.pi / 2, fade)[:, None]
head, tail = x[:i1], x[i2:]
y = np.concatenate([head[:-fade], head[-fade:] * np.cos(tt) + tail[:fade] * np.sin(tt), tail[fade:]])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", dst], input=y.astype(np.float32).tobytes(), check=True)
print(f"splice at {t1:.2f} s -> jump to {i2 / SR:.3f} s (skip {(i2 - i1) / SR:.3f} s); envelope r {s:.3f}, waveform r {c:.3f}; length {len(y) / SR:.2f} s")
