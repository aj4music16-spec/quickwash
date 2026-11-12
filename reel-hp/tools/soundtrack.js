// "The $99 Tag" - music bed and sound design, synthesized in plain Node (no packages).
// 100 BPM (18 frames a beat at 30 fps), 19.8 s = 594 frames = 33 beats, in E.
// A finger-picked, Piedmont-blues-leaning acoustic guitar (Karplus-Strong plucked strings:
// a short noise burst through a delay line of SR/f samples with a low-pass in the loop),
// alternating thumb bass under a syncopated treble riff; dry kick and upright-style sine bass
// from f18; the hole-punch "chunk" (low thud + click) on f108, 144, 180, 216, 252, 288 and f516,
// a single bell hit on f336 (the tag lands back side up), a held E chord from f504, last kick f576.
// The master is measured in-script (ITU-R BS.1770 K-weighted, gated) and set to -14 LUFS
// integrated, then peak-limited to -2.2 dBFS sample peak so the true peak stays under -1 dBTP.
// Usage: node tools/soundtrack.js out.wav
"use strict";
const fs = require("fs");
const SR = 48000, DUR = 19.8, N = Math.round(SR * DUR), BEAT = 60 / 100, TAU = 2 * Math.PI;
const fr = (f) => f / 30, bt = (b) => b * BEAT;
const mk = () => [new Float32Array(N), new Float32Array(N)];
const GTR = mk(), RHY = mk(), FX = mk();
let seed = 99001; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const noise = () => rnd() * 2 - 1, mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
const add = (B, i, l, r = l) => { if (i >= 0 && i < N) { B[0][i] += l; B[1][i] += r; } };
const lpA = (fc) => 1 - Math.exp(-TAU * fc / SR);
const sm = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

/* ---------------- instruments ---------------- */
// Karplus-Strong plucked string. loss = loop gain per period (ring length), tone = pick brightness (Hz).
function pluck(B, t, m, g, { len = 1.6, loss = 0.996, tone = 3200, pan = 0.5, mute = 0.025 } = {}) {
  const f = mtof(m), P = Math.max(2, Math.round(SR / f)), buf = new Float32Array(P);
  let lp = 0; for (let k = 0; k < P; k++) { lp += lpA(tone) * (noise() - lp); buf[k] = lp; }
  let mean = 0; for (let k = 0; k < P; k++) mean += buf[k]; mean /= P; for (let k = 0; k < P; k++) buf[k] -= mean;
  const i0 = Math.round(t * SR), L = Math.round(len * SR); let idx = 0, prev = 0, body = 0;
  for (let j = 0; j < L; j++) {
    const y = buf[idx]; buf[idx] = loss * 0.5 * (y + prev); prev = y; idx = (idx + 1) % P;
    body += lpA(5200) * (y - body);
    const env = 1 - sm(j, L - mute * SR, L), v = body * env * g;
    add(B, i0 + j, v * (1 - pan) * 2, v * pan * 2);
  }
}
function kick(B, t, g) { const i0 = Math.round(t * SR); let ph = 0;
  for (let j = 0; j < SR * 0.35; j++) { const tt = j / SR; ph += TAU * (48 + 90 * Math.exp(-tt / 0.03)) / SR;
    add(B, i0 + j, (Math.sin(ph) * Math.exp(-tt / 0.12) + (tt < 0.003 ? noise() * 0.3 : 0)) * g); } }
// upright-style bass: sine + a little 2nd harmonic, finger attack, woody decay
function ubass(B, t, m, g, len = 0.55) { const i0 = Math.round(t * SR), f = mtof(m); let lp = 0;
  for (let j = 0; j < SR * len; j++) { const tt = j / SR;
    const x = Math.sin(TAU * f * tt) + 0.25 * Math.sin(TAU * 2 * f * tt) + 0.08 * Math.sin(TAU * 3 * f * tt);
    lp += lpA(900) * (x - lp); const env = sm(tt, 0, 0.008) * Math.exp(-tt / 0.32) * (1 - sm(tt, len - 0.05, len));
    add(B, i0 + j, lp * env * g, lp * env * g * 0.94); } }
function shaker(B, t, g, pan = 0.62) { const i0 = Math.round(t * SR); let lp = 0, hp = 0;
  for (let j = 0; j < SR * 0.07; j++) { const x = noise(); lp += lpA(9000) * (x - lp); hp += lpA(3500) * (lp - hp);
    const v = (lp - hp) * sm(j / SR, 0, 0.012) * Math.exp(-(j / SR) / 0.025) * g; add(B, i0 + j, v * (1 - pan) * 2, v * pan * 2); } }
// the hole punch: a short low thud plus a steel click
function chunk(B, t, g) { const i0 = Math.round(t * SR); let ph = 0, lp = 0, hp = 0;
  for (let j = 0; j < SR * 0.16; j++) { const tt = j / SR; ph += TAU * (62 + 70 * Math.exp(-tt / 0.012)) / SR;
    const thud = Math.sin(ph) * Math.exp(-tt / 0.045);
    const x = noise(); lp += lpA(7000) * (x - lp); hp += lpA(1800) * (lp - hp);
    const click = (hp * 1.6 + Math.sin(TAU * 2900 * tt) * 0.5) * Math.exp(-tt / 0.004);
    add(B, i0 + j, (thud * 0.9 + click) * g); } }
function bell(B, t, m, g, dec = 1.1) { const i0 = Math.round(t * SR), f = mtof(m);
  [[1, 1, 1], [2.76, 0.45, 0.6], [5.4, 0.22, 0.35], [8.93, 0.08, 0.2]].forEach(([r, a, d]) => {
    for (let j = 0; j < SR * 3; j++) { const tt = j / SR; const v = Math.sin(TAU * f * r * tt) * Math.exp(-tt / (dec * d)) * a * g * sm(tt, 0, 0.002);
      add(B, i0 + j, v * 0.9, v); } }); }

/* ---------------- the riff ---------------- */
// chord per beat index (33 beats). E for 2 bars, A, E, B7 into the payoff, E, A (S10), E, B7 turnaround, E held.
const CH = {
  E:  { thumb: [40, 52], treble: [[0.5, 67], [1.5, 71], [2, 64], [2.5, 67], [3, 68], [3.5, 64]] },
  A:  { thumb: [45, 52], treble: [[0.5, 72], [1.5, 76], [2, 69], [2.5, 72], [3, 73], [3.5, 69]] },
  B7: { thumb: [47, 54], treble: [[0.5, 75], [1.5, 78], [2, 69], [2.5, 71], [3, 75], [3.5, 71]] },
};
const BAR = ["E", "E", "A", "E", "B7", "E", "A", "B7"];   // bar n covers beats 4n..4n+3 (bar 4 = beats 16-19: B7 for 16-17 only)
const chordAt = (b) => b < 16 ? BAR[Math.floor(b / 4)] : b < 18 ? "B7" : b < 22 ? "E" : b < 26 ? "A" : b < 27 ? "E" : b < 28 ? "B7" : "E";
const SW = 0.58;                                          // light shuffle on the off-eighths
const swing = (o) => (o % 1 === 0.5 ? Math.floor(o) + SW : o);

for (let b = 0; b < 28; b++) {
  const c = CH[chordAt(b)], t = bt(b), full = b >= 18;
  // alternating thumb: root on 1 and 3, the upper bass note on 2 and 4 (palm-muted, short)
  pluck(GTR, t, c.thumb[b % 2], 0.5, { len: 0.42, loss: 0.985, tone: 1400, pan: 0.42, mute: 0.04 });
  // treble fingers: the events in this beat of the bar pattern
  const beatInBar = b % 4;
  c.treble.filter(([o]) => Math.floor(o) === beatInBar).forEach(([o, m]) => {
    pluck(GTR, bt(b - beatInBar + swing(o)), m, full ? 0.34 : 0.3, { len: 1.1, loss: 0.996, tone: 3600, pan: 0.6 });
  });
  // the riff resolves on beat 18 (f324): a full E strum
  if (b === 18) [40, 47, 52, 56, 59, 64].forEach((m, k) => pluck(GTR, t + k * 0.011, m, 0.26, { len: 1.6, loss: 0.997, tone: 3000, pan: 0.35 + k * 0.05 }));
  // full band from the payoff: a brushed chord on 2 and 4, shaker eighths
  if (full && b % 2 === 1) { const ch = chordAt(b) === "A" ? [45, 52, 57, 61, 64] : chordAt(b) === "B7" ? [47, 54, 57, 63, 66] : [40, 47, 52, 56, 59];
    ch.forEach((m, k) => pluck(GTR, t + k * 0.008, m + 12, 0.1, { len: 0.3, loss: 0.99, tone: 2600, pan: 0.66, mute: 0.05 })); }
  if (full) { shaker(RHY, t, 0.05); shaker(RHY, t + SW * BEAT, 0.035); }
  // kick and upright bass from beat 1 (f18)
  if (b >= 1) {
    kick(RHY, t, full ? 0.62 : b % 2 === 0 ? 0.5 : 0.36);
    const root = c.thumb[0] - 12, fifth = root + 7;
    ubass(RHY, t, b % 2 === 0 ? root : fifth, full ? 0.42 : 0.34);
    if (full && b % 2 === 1) ubass(RHY, t + SW * BEAT, root + 12, 0.2, 0.25);   // a walking pickup
  }
}
// beat 28 (f504): one held E chord, kicks on 28, 30, 32 (f576 is the last), ring out to f594
{ const t0 = bt(28);
  [40, 47, 52, 56, 59, 64].forEach((m, k) => pluck(GTR, t0 + k * 0.016, m, 0.42, { len: DUR - t0 - k * 0.016, loss: 0.9993, tone: 3200, pan: 0.32 + k * 0.07, mute: 0.3 }));
  pluck(GTR, t0 + 0.12, 71, 0.18, { len: DUR - t0 - 0.12, loss: 0.9992, tone: 4000, pan: 0.7, mute: 0.3 });
  [28, 30, 32].forEach((b, k) => { kick(RHY, bt(b), [0.66, 0.5, 0.44][k]); ubass(RHY, bt(b), 28, [0.44, 0.3, 0.26][k], 1.0); });
}

/* ---------------- sound design, on the picture ---------------- */
[108, 144, 180, 216, 252, 288, 516].forEach((f) => chunk(FX, fr(f), 0.44));   // -3 dB under the kick (0.62)
bell(FX, fr(336), 88, 0.16); bell(FX, fr(336) + 0.004, 95, 0.05);              // the tag lands back side up

/* ---------------- master ---------------- */
const L = new Float32Array(N), R = new Float32Array(N);
for (let i = 0; i < N; i++) { const t = i / SR, fo = 1 - sm(t, DUR - 0.35, DUR), fi = sm(t, 0, 0.004);
  L[i] = (GTR[0][i] * 0.9 + RHY[0][i] + FX[0][i]) * fo * fi; R[i] = (GTR[1][i] * 0.9 + RHY[1][i] + FX[1][i]) * fo * fi; }

function biquad(x, b, a) { const y = new Float32Array(x.length); let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) { const v = b[0] * x[i] + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2; x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v; } return y; }
function lufs(Lc, Rc) {  // BS.1770-4 integrated loudness at 48 kHz
  const s1b = [1.53512485958697, -2.69169618940638, 1.19839281085285], s1a = [1, -1.69065929318241, 0.73248077421585];
  const s2b = [1, -2, 1], s2a = [1, -1.99004745483398, 0.99007225036621];
  const kl = biquad(biquad(Lc, s1b, s1a), s2b, s2a), kr = biquad(biquad(Rc, s1b, s1a), s2b, s2a);
  const blk = Math.round(0.4 * SR), hop = Math.round(0.1 * SR), z = [];
  for (let s = 0; s + blk <= N; s += hop) { let acc = 0; for (let i = s; i < s + blk; i++) acc += kl[i] * kl[i] + kr[i] * kr[i]; z.push(acc / blk); }
  const ld = (p) => -0.691 + 10 * Math.log10(p);
  const g1 = z.filter((p) => ld(p) > -70), m1 = g1.reduce((a, b) => a + b, 0) / g1.length;
  const g2 = g1.filter((p) => ld(p) > ld(m1) - 10); return ld(g2.reduce((a, b) => a + b, 0) / g2.length);
}
let maxGR = 0;
function limit(Lc, Rc, ceil) {  // look-ahead peak limiter: 1.5 ms look-ahead, 60 ms release
  const la = Math.round(0.0015 * SR), need = new Float32Array(N);
  for (let i = 0; i < N; i++) { const p = Math.max(Math.abs(Lc[i]), Math.abs(Rc[i])); need[i] = p > ceil ? ceil / p : 1; }
  let g = 1; const rel = 1 - Math.exp(-1 / (0.06 * SR));
  for (let i = 0; i < N; i++) { let m = 1; for (let j = i; j <= Math.min(N - 1, i + la); j++) if (need[j] < m) m = need[j];
    g = m < g ? m : g + (m - g) * rel; maxGR = Math.max(maxGR, -20 * Math.log10(g)); Lc[i] *= g; Rc[i] *= g; }
}
const CEIL = Math.pow(10, -2.2 / 20);
for (let pass = 0; pass < 3; pass++) { const k = Math.pow(10, (-14 - lufs(L, R)) / 20); for (let i = 0; i < N; i++) { L[i] *= k; R[i] *= k; } limit(L, R, CEIL); }
let peak = 0; for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));

const buf = Buffer.alloc(44 + N * 4);
buf.write("RIFF", 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write("WAVEfmt ", 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(N * 4, 40);
const q = (v) => Math.max(-32768, Math.min(32767, Math.round(v * 32767)));
for (let i = 0; i < N; i++) { buf.writeInt16LE(q(L[i]), 44 + i * 4); buf.writeInt16LE(q(R[i]), 46 + i * 4); }
fs.writeFileSync(process.argv[2] || "bed.wav", buf);
console.log("wrote", process.argv[2] || "bed.wav", "seconds", (N / SR).toFixed(3), "LUFS(in-script)", lufs(L, R).toFixed(2), "sample peak dBFS", (20 * Math.log10(peak)).toFixed(2), "max limiter GR dB", maxGR.toFixed(1));
