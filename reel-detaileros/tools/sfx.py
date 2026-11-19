"""Synthesize the reel's sound effects as 44.1 kHz mono WAVs (no samples or licences needed).

usage: python3 sfx.py <out_dir>
"""
import os, sys, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def env(t, attack, decay):
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay)


def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be a scalar or a per-sample array (Hz)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    alpha = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc); y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def sweep_sine(t, f0, f1, curve=1.0):
    f = f0 + (f1 - f0) * (t / t[-1]) ** curve
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def ding():
    # two bright bell notes, like a message chime
    out = np.zeros(int(0.9 * SR))
    for start, f in ((0.0, 1318.5), (0.11, 1760.0)):
        t = t_axis(0.9 - start)
        tone = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3.01 * f * t))
        s = int(start * SR); out[s:s + len(t)] += tone * env(t, 0.004, 0.22)
    return out * 0.5


def whoosh(sec=0.55, lo=300, hi=5000):
    t = t_axis(sec); n = rng.standard_normal(len(t))
    shape = np.sin(np.pi * t / sec) ** 1.6
    cut = lo + (hi - lo) * np.sin(np.pi * t / sec)
    return highpass(lowpass(n, cut), 120) * shape * 0.6


def pop():
    t = t_axis(0.16)
    return sweep_sine(t, 950, 260, 0.5) * env(t, 0.002, 0.045) * 0.8


def tap():
    t = t_axis(0.06)
    click = highpass(rng.standard_normal(len(t)), 2500) * env(t, 0.0005, 0.006)
    body = np.sin(2 * np.pi * 1900 * t) * env(t, 0.0008, 0.012)
    return (click * 0.6 + body * 0.5)


def tick():
    t = t_axis(0.05)
    return np.sin(2 * np.pi * 3200 * t) * env(t, 0.0008, 0.01) * 0.5


def kaching():
    out = np.zeros(int(1.3 * SR))
    # "cha": short metallic noise burst
    t = t_axis(0.09); out[:len(t)] += highpass(rng.standard_normal(len(t)), 3000) * env(t, 0.001, 0.025) * 0.5
    # "ching": bright inharmonic bell partials
    s = int(0.07 * SR); t = t_axis(1.3 - 0.07)
    bell = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((2093, 1.0), (2637, 0.7), (3136, 0.55), (4186, 0.3), (5274, 0.18)))
    out[s:s + len(t)] += bell * env(t, 0.002, 0.32) * 0.35
    return out


def impact():
    t = t_axis(1.8)
    boom = sweep_sine(t, 95, 38, 0.35) * env(t, 0.003, 0.45)
    thump = lowpass(rng.standard_normal(len(t)), 220) * env(t, 0.001, 0.08) * 3.0
    shimmer = highpass(rng.standard_normal(len(t)), 6000) * env(t, 0.02, 0.5) * 0.06
    return (boom + thump + shimmer) * 0.8


def write(path, x):
    x = x / max(1e-9, np.max(np.abs(x))) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for name, fn in (("ding", ding), ("whoosh", whoosh), ("pop", pop), ("tap", tap), ("tick", tick),
                     ("kaching", kaching), ("impact", impact)):
        write(os.path.join(out, name + ".wav"), fn()); print("ok", name)
