// Synthesizes the reel's music bed + sound design (120 BPM, cuts on the beat).
// Usage: node tools/soundtrack.js assets/audio/bed.wav
const fs = require('fs');
const SR = 44100, DUR = 18, N = SR * DUR, BEAT = 0.5;
const L = new Float32Array(N), R = new Float32Array(N);
let seed = 4242; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const noise = () => rnd() * 2 - 1, mtof = m => 440 * Math.pow(2, (m - 69) / 12);
const add = (i, l, r = l) => { if (i >= 0 && i < N) { L[i] += l; R[i] += r; } };
const sm = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lpA = fc => 1 - Math.exp(-2 * Math.PI * fc / SR);

// sections: hook 0-2 (tension), app 2-7.5, come 7.5-10.5, prices 10.5-13, proof 13-15, end 15-18
const chordAt = t => t < 2 ? [45, 52, 57, 60] : t < 7.5 ? (Math.floor((t - 2) / 2) % 2 ? [41, 53, 57, 60, 64] : [45, 52, 57, 60, 64])
  : t < 10.5 ? [48, 55, 60, 64, 67] : t < 13 ? [43, 55, 59, 62, 67] : t < 15 ? [41, 53, 57, 60, 65] : [48, 55, 60, 64, 67, 72];
// pad
{ const lp = new Float32Array(8); for (let i = 0; i < N; i++) { const t = i / SR, ch = chordAt(t); let v = 0;
    ch.forEach((m, k) => { const f = mtof(m); v += Math.sin(2 * Math.PI * f * t) + .4 * Math.sin(2 * Math.PI * f * 1.003 * t + k) + .15 * Math.sin(4 * Math.PI * f * t); });
    const env = (t < 2 ? .5 * sm(t, 0, .3) : 1) * (1 - sm(t, 17.2, 18));
    const duck = 1 - .35 * Math.exp(-((t % BEAT)) * 14) * (t >= 2 ? 1 : 0);
    v = v / ch.length * .11 * env * duck; add(i, v, v); } }
// plucky arp on 8ths from the app scene on
for (let t = 2; t < 17; t += BEAT / 2) { const ch = chordAt(t), n = ch[1 + (Math.round(t * 4) % (ch.length - 1))] + 12, f = mtof(n), i0 = Math.floor(t * SR), pan = (Math.round(t * 4) % 2) ? .3 : .7;
  const g = t < 7.5 ? .05 : t < 15 ? .065 : .05;
  for (let j = 0; j < SR * .22; j++) { const tt = j / SR, v = (Math.sin(2 * Math.PI * f * tt) + .3 * Math.sin(4 * Math.PI * f * tt)) * Math.exp(-tt * 16) * g; add(i0 + j, v * (1 - pan) * 2, v * pan * 2); } }
// kick on every beat, clap on 2 & 4, hats on off-8ths, bass on the root
for (let b = 0; b * BEAT < 17.4; b++) { const t = b * BEAT; if (t < 2) continue; const i0 = Math.floor(t * SR); let ph = 0;
  for (let j = 0; j < SR * .3; j++) { const tt = j / SR; ph += 2 * Math.PI * (48 + 90 * Math.exp(-tt * 34)) / SR; add(i0 + j, Math.sin(ph) * Math.exp(-tt * 10) * .42); }
  const root = mtof(chordAt(t)[0] - 12); for (let j = 0; j < SR * .42; j++) { const tt = j / SR; add(i0 + j, Math.sin(2 * Math.PI * root * tt) * Math.exp(-tt * 5) * sm(tt, 0, .01) * .2); }
  if (b % 2 === 1) { let lp = 0; for (let j = 0; j < SR * .14; j++) { const x = noise(); lp += lpA(2600) * (x - lp); const v = lp * Math.exp(-j / SR * 30) * .32; add(i0 + j, v, v * .9); } }
  const h0 = Math.floor((t + BEAT / 2) * SR); let lp = 0; for (let j = 0; j < SR * .04; j++) { const x = noise(); lp += lpA(8000) * (x - lp); const v = (x - lp) * Math.exp(-j / SR * 90) * .09; add(h0 + j, v * .6, v); } }
// hook: heartbeat thumps + riser into the drop at 2.0
[0, .5, 1.0, 1.5].forEach(t => { const i0 = Math.floor(t * SR); let ph = 0; for (let j = 0; j < SR * .25; j++) { const tt = j / SR; ph += 2 * Math.PI * (55 + 40 * Math.exp(-tt * 30)) / SR; add(i0 + j, Math.sin(ph) * Math.exp(-tt * 12) * .3); } });
function whoosh(c, len = .45, g = .26) { const i0 = Math.floor((c - len) * SR); let lp = 0; for (let j = 0; j < SR * (len + .2); j++) { const tt = j / SR, k = tt < len ? tt / len : 1 - (tt - len) / .2; lp += lpA(300 + 6000 * k * k) * (noise() - lp); const v = lp * k * k * g, p = tt / (len + .2); add(i0 + j, v * (1.2 - p), v * (.2 + p)); } }
whoosh(2.0, .9, .34); [7.5, 9.2, 10.5, 13.0, 15.0].forEach(c => whoosh(c));
// UI taps (3.27, 4.7), screen slides, pops on steps/cards/stars, success + logo chimes
const blip = (t, f, g = .14, d = 60) => { const i0 = Math.floor(t * SR); for (let j = 0; j < SR * .09; j++) { const tt = j / SR; add(i0 + j, Math.sin(2 * Math.PI * f * tt) * Math.exp(-tt * d) * g); } };
blip(3.28, 1500); blip(4.71, 1500); [2.72, 4.02, 5.42].forEach(t => blip(t, 880, .09, 40));
[10.74, 10.84, 10.94].forEach((t, k) => blip(t, 520 + k * 130, .13, 35)); [13.55, 13.62, 13.69, 13.76, 13.83].forEach((t, k) => blip(t, 900 + k * 120, .1, 45));
const bell = (t, m, g) => { const i0 = Math.floor(t * SR), b = mtof(m); [[1, 1], [2.01, .45], [3, .2]].forEach(([r, a]) => { for (let j = 0; j < SR * 2; j++) { const tt = j / SR; add(i0 + j, Math.sin(2 * Math.PI * b * r * tt) * Math.exp(-tt * (3 + r)) * a * g); } }); };
bell(6.57, 76, .1); bell(6.67, 81, .08); bell(15.22, 84, .1); bell(15.34, 88, .07); bell(15.46, 91, .06);
// master
let peak = 0; for (let i = 0; i < N; i++) { const fo = 1 - sm(i / SR, 17.3, 18); L[i] = Math.tanh(L[i] * 1.25 * fo); R[i] = Math.tanh(R[i] * 1.25 * fo); peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i])); }
const k = .89 / peak, buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(L[i] * k * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(R[i] * k * 32767), 46 + i * 4); }
fs.writeFileSync(process.argv[2], buf); console.log('wrote', process.argv[2]);
