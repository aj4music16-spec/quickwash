#!/usr/bin/env python3
"""Beat grid + onsets for an audio (or video) file, numpy only.

    python3 -I beats.py <audio> [--start S] [--dur D] [--bpm-min 70 --bpm-max 180] [--json out.json]

Prints tempo (BPM), the beat-grid phase (time of the first beat) and the strongest onsets.
Method: ffmpeg -> 22.05 kHz mono, STFT (2048/512), half-wave-rectified log spectral flux,
tempo from the autocorrelation of the flux envelope, phase by maximising flux on the grid.
"""
import argparse, json, subprocess, sys
import numpy as np

SR, N, HOP = 22050, 2048, 512


def load(path, start=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


def flux(x):
    win = np.hanning(N).astype(np.float32)
    n = 1 + max(0, (len(x) - N) // HOP)
    frames = np.lib.stride_tricks.as_strided(x, (n, N), (x.strides[0] * HOP, x.strides[0]))
    mag = np.log1p(100 * np.abs(np.fft.rfft(frames * win, axis=1)))
    f = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    f = np.concatenate([[0], f])
    # subtract local mean (adaptive threshold) and normalise
    k = 16
    loc = np.convolve(f, np.ones(2 * k + 1) / (2 * k + 1), mode="same")
    o = np.maximum(0, f - loc)
    return o / (o.max() + 1e-9)


def analyse(path, start=None, dur=None, bmin=70, bmax=180):
    x = load(path, start, dur)
    o = flux(x)
    fps = SR / HOP
    ac = np.correlate(o, o, mode="full")[len(o) - 1:]
    lags = np.arange(len(ac))
    lo, hi = int(fps * 60 / bmax), int(fps * 60 / bmin)
    lag = lo + int(np.argmax(ac[lo:hi + 1]))
    # refine with parabolic interpolation
    if lo < lag < hi:
        a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
        lagf = lag + 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
    else:
        lagf = float(lag)
    period = lagf / fps
    # phase: best offset of a comb over the envelope
    t = np.arange(len(o)) / fps
    best, phase = -1, 0.0
    for ph in np.arange(0, period, 0.005):
        g = np.arange(ph, t[-1], period)
        idx = np.clip(np.round(g * fps).astype(int), 0, len(o) - 1)
        s = o[idx].sum()
        if s > best:
            best, phase = s, ph
    # onsets: local maxima above 0.25
    pk = [i for i in range(2, len(o) - 2) if o[i] > 0.25 and o[i] == o[i - 2:i + 3].max()]
    onsets = [{"t": round(i / fps, 3), "s": round(float(o[i]), 2)} for i in pk]
    # refine the phase from the strong onsets themselves (circular mean of t mod period):
    # the comb search above is quantised to the 23 ms hop, the onsets carry the real attack times
    strong = [d["t"] for d in onsets if d["s"] >= 0.5]
    if len(strong) >= 3:
        ang = 2 * np.pi * (np.array(strong) % period) / period
        phase = float((np.angle(np.exp(1j * ang).mean()) % (2 * np.pi)) / (2 * np.pi) * period)
    return {"bpm": round(60 / period, 2), "period": round(period, 4), "phase": round(phase, 3),
            "duration": round(len(x) / SR, 3), "onsets": onsets}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--start", type=float)
    ap.add_argument("--dur", type=float)
    ap.add_argument("--bpm-min", type=float, default=70)
    ap.add_argument("--bpm-max", type=float, default=180)
    ap.add_argument("--json")
    a = ap.parse_args()
    r = analyse(a.audio, a.start, a.dur, a.bpm_min, a.bpm_max)
    if a.json:
        json.dump(r, open(a.json, "w"), indent=1)
    print(f"bpm {r['bpm']}  period {r['period']} s  first beat {r['phase']} s  dur {r['duration']} s")
    strong = sorted(r["onsets"], key=lambda d: -d["s"])[:24]
    print("strongest onsets:", ", ".join(f"{d['t']}({d['s']})" for d in sorted(strong, key=lambda d: d["t"])))
