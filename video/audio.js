// Synthesizes the soundtrack for "The Reset" as a 44.1 kHz stereo WAV.
// Score + sound design are timed to the same cue sheet as index.html.
// Usage: node audio.js out.wav
const fs = require('fs');
const SR = 44100, DUR = 40, N = SR * DUR;
const L = new Float32Array(N), Rch = new Float32Array(N);

let seed = 12345;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const noise = () => rnd() * 2 - 1;
const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
const add = (i, l, r = l) => { if (i >= 0 && i < N) { L[i] += l; Rch[i] += r; } };
const smooth = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lpA = fc => 1 - Math.exp(-2 * Math.PI * fc / SR);

/* ---------- warm pad: chord progression ---------- */
// [start, end, midi notes, gain]
const chords = [
  [0.0, 4.2, [53, 57, 60, 64], .9],       // Fmaj7  — curiosity
  [4.0, 9.2, [53, 60, 64, 67, 69], 1.0],  // Fmaj9  — first drive glow
  [9.0, 15.2, [50, 57, 60, 65], .8],      // Dm7    — nostalgia
  [15.0, 21.2, [46, 53, 57, 62], .9],     // Bbmaj7 — life happens
  [21.0, 29.2, [48, 55, 60, 64, 67], 1.0],// Cadd9  — the reset
  [29.0, 35.4, [43, 55, 60, 62, 67], 1.0],// Gsus   — it comes to you
  [36.3, 40.0, [41, 53, 57, 60, 64, 67], 1.1], // Fmaj9 — resolve
];
for (const [a, b, notes, g] of chords) {
  const i0 = Math.floor(a * SR), i1 = Math.floor(b * SR);
  notes.forEach((m, k) => {
    const f = mtof(m), det = 1 + (k % 2 ? .0025 : -.002);
    let lp = 0; const A = lpA(1800);
    for (let i = i0; i < i1; i++) {
      const t = i / SR, lt = t - a;
      const env = smooth(lt, 0, .6) * (1 - smooth(t, b - .5, b));
      const trem = 1 + .08 * Math.sin(2 * Math.PI * (.3 + k * .07) * t);
      let x = Math.sin(2 * Math.PI * f * t) + .5 * Math.sin(2 * Math.PI * f * det * t) + .18 * Math.sin(4 * Math.PI * f * t);
      lp += A * (x - lp);
      const v = lp * env * trem * g * .028;
      const pan = .5 + (k / notes.length - .5) * .6;
      add(i, v * (1 - pan) * 2, v * pan * 2);
    }
  });
}

/* ---------- pulse (kick + soft hats) from "life happens" to the door shut ---------- */
const BEAT = 60 / 96;
for (let t = 15.0; t < 35.3; t += BEAT) {
  const g = t < 21 ? .45 : .7;
  const i0 = Math.floor(t * SR);
  let ph = 0;
  for (let j = 0; j < SR * .35; j++) {
    const tt = j / SR, f = 45 + 80 * Math.exp(-tt * 30); ph += 2 * Math.PI * f / SR;
    add(i0 + j, Math.sin(ph) * Math.exp(-tt * 9) * .32 * g);
  }
  if (t >= 21) { // offbeat hat
    const h0 = Math.floor((t + BEAT / 2) * SR); let lp = 0;
    for (let j = 0; j < SR * .05; j++) { const x = noise(); lp += lpA(7000) * (x - lp); const v = (x - lp) * Math.exp(-j / SR * 80) * .07; add(h0 + j, v * .7, v); }
  }
}

/* ---------- whooshes into cuts ---------- */
for (const c of [1.35, 2.7, 9.0, 15.0, 21.0, 25.0, 29.0]) {
  const len = .45, i0 = Math.floor((c - len) * SR); let lp = 0;
  for (let j = 0; j < SR * (len + .25); j++) {
    const tt = j / SR, k = tt < len ? tt / len : 1 - (tt - len) / .25;
    lp += lpA(300 + 5000 * k * k) * (noise() - lp);
    const v = lp * k * k * .22, pan = tt / (len + .25);
    add(i0 + j, v * (1.2 - pan), v * (.2 + pan));
  }
}

/* ---------- door open (4.15s) and door shut (35.42s) ---------- */
function thump(t, gain, freq, decay) {
  const i0 = Math.floor(t * SR); let lp = 0, ph = 0;
  for (let j = 0; j < SR * .8; j++) {
    const tt = j / SR; ph += 2 * Math.PI * (freq + 40 * Math.exp(-tt * 40)) / SR;
    lp += lpA(400) * (noise() - lp);
    add(i0 + j, (Math.sin(ph) * Math.exp(-tt * decay) + lp * 1.5 * Math.exp(-tt * 25)) * gain);
  }
}
function click(t, gain) { const i0 = Math.floor(t * SR); for (let j = 0; j < SR * .03; j++) add(i0 + j, noise() * Math.exp(-j / SR * 200) * gain); }
click(4.12, .25); thump(4.15, .12, 90, 14);
click(35.40, .35); thump(35.42, .6, 52, 7);

/* ---------- archival section: projector flutter + crackle ---------- */
for (let i = Math.floor(9.0 * SR); i < 15.0 * SR; i++) {
  const t = i / SR, env = smooth(t, 9, 9.4) * (1 - smooth(t, 14.6, 15));
  add(i, (rnd() < .0009 ? noise() * .25 : 0) * env + Math.sin(2 * Math.PI * 18 * t) * noise() * .006 * env);
}

/* ---------- foam (bubble pops) 21–23.5, rinse 23–25 ---------- */
for (let n = 0; n < 220; n++) {
  const t = 21 + rnd() * 2.6, f = 900 + rnd() * 2600, i0 = Math.floor(t * SR), g = .03 + rnd() * .05, pan = rnd();
  for (let j = 0; j < SR * .025; j++) { const tt = j / SR; const v = Math.sin(2 * Math.PI * f * (1 + tt * 30) * tt) * Math.exp(-tt * 260) * g; add(i0 + j, v * (1 - pan) * 2, v * pan * 2); }
}
{ let lp = 0, lp2 = 0; for (let i = Math.floor(21 * SR); i < 25.2 * SR; i++) {
  const t = i / SR, env = smooth(t, 21, 21.6) * .25 + smooth(t, 22.8, 23.6) * (1 - smooth(t, 24.6, 25.1)) * .75;
  const x = noise(); lp += lpA(3500) * (x - lp); lp2 += lpA(500) * (lp - lp2); const v = (lp - lp2) * env * .32; add(i, v, v * .9);
}}
/* ---------- brush strokes (left) + microfiber swish (right) 25–29 ---------- */
{ let lp = 0, lp2 = 0; for (let i = Math.floor(25 * SR); i < 29 * SR; i++) {
  const t = i / SR, bt = t - 25, env = smooth(t, 25, 25.3) * (1 - smooth(t, 28.6, 29));
  const strokes = Math.pow(Math.abs(Math.sin(bt * 11)), 3);
  const x = noise(); lp += lpA(6000) * (x - lp); lp2 += lpA(1500) * (lp - lp2);
  const brush = (lp - lp2) * strokes * .16 * env;
  const swish = lp2 * (.5 + .5 * Math.sin(bt * 3)) * .18 * env;
  add(i, brush + swish * .3, brush * .3 + swish);
}}

/* ---------- end card: logo chime (37.1) + CTA pop (37.7) ---------- */
function bell(t, base, gain) {
  const i0 = Math.floor(t * SR);
  [[1, 1], [2.01, .5], [3.0, .25], [4.2, .12]].forEach(([r, a]) => {
    for (let j = 0; j < SR * 2.8; j++) { const tt = j / SR; add(i0 + j, Math.sin(2 * Math.PI * base * r * tt) * Math.exp(-tt * (2.2 + r)) * a * gain); }
  });
}
bell(37.1, mtof(84), .09); bell(37.22, mtof(88), .06); bell(37.34, mtof(91), .05);
{ const i0 = Math.floor(37.7 * SR); for (let j = 0; j < SR * .12; j++) { const tt = j / SR; add(i0 + j, Math.sin(2 * Math.PI * (300 + 900 * tt * 8) * tt) * Math.exp(-tt * 40) * .12); } }

/* ---------- master: gentle fade out, soft clip, normalize ---------- */
let peak = 0;
for (let i = 0; i < N; i++) {
  const t = i / SR, fo = 1 - smooth(t, 39.2, 40);
  L[i] = Math.tanh(L[i] * 1.3 * fo); Rch[i] = Math.tanh(Rch[i] * 1.3 * fo);
  peak = Math.max(peak, Math.abs(L[i]), Math.abs(Rch[i]));
}
const norm = .89 / peak;
const buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8); buf.write('fmt ', 12);
buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(L[i] * norm * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(Rch[i] * norm * 32767), 46 + i * 4); }
fs.writeFileSync(process.argv[2] || 'soundtrack.wav', buf);
console.log('wrote', process.argv[2] || 'soundtrack.wav', 'peak', peak.toFixed(3));
