// Synthesizes the reel's music bed and sound design: a Jersey-club-style beat at 144 BPM
// (kick on 16th steps 0, 4, 8, 11, 14), locked to the picture's beat grid.
// Usage: node tools/soundtrack.js out.wav
const fs = require('fs');
const SR = 44100, DUR = 575 / 30, N = Math.round(SR * DUR), BEAT = 60 / 144, STEP = BEAT / 4;
const mk = () => [new Float32Array(N), new Float32Array(N)];
const M = mk(), X = mk();                       // music bus, effects bus
let seed = 20261110; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const noise = () => rnd() * 2 - 1, mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
const add = (B, i, l, r = l) => { if (i >= 0 && i < N) { B[0][i] += l; B[1][i] += r; } };
const sm = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lpA = (fc) => 1 - Math.exp(-2 * Math.PI * fc / SR);
const TAU = 2 * Math.PI;

/* ---------------- instruments ---------------- */
function kick(B, t, g) { const i0 = Math.round(t * SR); let ph = 0;
  for (let j = 0; j < SR * 0.4; j++) { const tt = j / SR; ph += TAU * (47 + 115 * Math.exp(-tt / 0.026)) / SR;
    add(B, i0 + j, (Math.sin(ph) * Math.exp(-tt / 0.15) + (tt < 0.004 ? noise() * 0.5 : 0)) * g); } }
function clap(B, t, g) { [0, 0.011, 0.023].forEach((o, k) => { const i0 = Math.round((t + o) * SR); let lp = 0, hp = 0;
  const len = k === 2 ? 0.16 : 0.03, dec = k === 2 ? 0.07 : 0.01;
  for (let j = 0; j < SR * len; j++) { const x = noise(); lp += lpA(3400) * (x - lp); hp += lpA(900) * (lp - hp); const v = (lp - hp) * Math.exp(-(j / SR) / dec) * g; add(B, i0 + j, v * 0.9, v); } }); }
function hat(B, t, g, open) { const i0 = Math.round(t * SR); let lp = 0; const dec = open ? 0.07 : 0.016;
  for (let j = 0; j < SR * (open ? 0.22 : 0.06); j++) { const x = noise(); lp += lpA(7500) * (x - lp); const v = (x - lp) * Math.exp(-(j / SR) / dec) * g; add(B, i0 + j, v * 0.7, v); } }
function bass(B, t, m, g) { const i0 = Math.round(t * SR), f = mtof(m);
  for (let j = 0; j < SR * 0.36; j++) { const tt = j / SR; add(B, i0 + j, (Math.sin(TAU * f * tt) + 0.18 * Math.sin(TAU * 2 * f * tt)) * sm(tt, 0, 0.006) * Math.exp(-tt / 0.2) * g); } }
function stab(B, t, notes, g) { notes.forEach((m, k) => { const i0 = Math.round(t * SR), f = mtof(m), pan = 0.35 + 0.15 * k; let lp = 0;
  for (let j = 0; j < SR * 0.3; j++) { const tt = j / SR; let x = 0; for (let h = 1; h <= 6; h++) x += Math.sin(TAU * f * h * tt + k) / h;
    lp += lpA(1500 + 2500 * Math.exp(-tt / 0.05)) * (x - lp); const v = lp * Math.exp(-tt / 0.085) * g; add(B, i0 + j, v * (1 - pan) * 2, v * pan * 2); } }); }
function pluck(B, t, m, g, pan) { const i0 = Math.round(t * SR), f = mtof(m);
  for (let j = 0; j < SR * 0.2; j++) { const tt = j / SR; const v = (Math.sin(TAU * f * tt) + 0.3 * Math.sin(TAU * 3 * f * tt)) * Math.exp(-tt / 0.06) * g; add(B, i0 + j, v * (1 - pan) * 2, v * pan * 2); } }
function bell(B, t, m, g, dec = 0.32) { const i0 = Math.round(t * SR), f = mtof(m);
  [[1, 1, 1], [2.76, 0.5, 0.7], [5.4, 0.25, 0.45], [8.93, 0.1, 0.3]].forEach(([r, a, d]) => { for (let j = 0; j < SR * 1.6; j++) { const tt = j / SR; add(B, i0 + j, Math.sin(TAU * f * r * tt) * Math.exp(-tt / (dec * d)) * a * g); } }); }
function thock(B, t, g, f = 170) { const i0 = Math.round(t * SR); let lp = 0, ph = 0;
  for (let j = 0; j < SR * 0.12; j++) { const tt = j / SR; ph += TAU * (f * (0.6 + 0.4 * Math.exp(-tt / 0.01))) / SR; lp += lpA(2600) * (noise() - lp);
    add(B, i0 + j, (Math.sin(ph) * Math.exp(-tt / 0.03) + lp * 0.7 * Math.exp(-tt / 0.008)) * g); } }
function tick(B, t, g, f = 2200, pan = 0.5) { const i0 = Math.round(t * SR); for (let j = 0; j < SR * 0.03; j++) { const tt = j / SR; const v = Math.sin(TAU * f * tt) * Math.exp(-tt / 0.006) * g; add(B, i0 + j, v * (1 - pan) * 2, v * pan * 2); } }
function blip(B, t, g, f = 1500) { const i0 = Math.round(t * SR); for (let j = 0; j < SR * 0.08; j++) { const tt = j / SR; add(B, i0 + j, Math.sin(TAU * f * tt) * Math.exp(-tt / 0.016) * g); } }
function pop(B, t, g) { const i0 = Math.round(t * SR); let ph = 0; for (let j = 0; j < SR * 0.1; j++) { const tt = j / SR; ph += TAU * (420 + 900 * Math.min(1, tt / 0.05)) / SR; add(B, i0 + j, Math.sin(ph) * Math.exp(-tt / 0.03) * g); } }
function whoosh(B, c, g, len = 0.3, tail = 0.3, f0 = 350, f1 = 5200) { const i0 = Math.round((c - len) * SR); let lp = 0, lp2 = 0;
  for (let j = 0; j < SR * (len + tail); j++) { const tt = j / SR, k = tt < len ? Math.pow(tt / len, 2) : Math.pow(1 - (tt - len) / tail, 1.5);
    lp += lpA(f0 + (f1 - f0) * k) * (noise() - lp); lp2 += lpA(180) * (lp - lp2); const v = (lp - lp2) * k * g, p = tt / (len + tail); add(B, i0 + j, v * (1.25 - p), v * (0.25 + p)); } }

/* ---------------- music ---------------- */
const CH = [ // F minor: i  VI  III  VII
  { bass: 29, stab: [65, 68, 72] }, { bass: 37, stab: [61, 65, 68] }, { bass: 32, stab: [63, 68, 72] }, { bass: 39, stab: [63, 67, 70] } ];
const KICK = [0, 4, 8, 11, 14], STAB = [0, 3, 6, 11, 14];
for (let bar = 0; bar * 4 < 38; bar++) {
  const ch = CH[bar % 4];
  for (let s = 0; s < 16; s++) {
    const beat = bar * 4 + s / 4, t = beat * BEAT; if (beat >= 38) break;
    const intro = beat < 4, old = beat >= 4 && beat < 8, full = beat >= 8;
    if (KICK.includes(s)) { kick(M, t, intro ? 0.42 : old ? 0.55 : 0.62); if (full) bass(M, t, ch.bass + 12, 0.3); }
    if ((s === 4 || s === 12) && !intro) clap(M, t, old ? 0.5 : 0.42);
    if (s % 2 === 0) hat(M, t, (s % 4 === 2 ? 0.1 : 0.06) * (intro ? 0.7 : 1), false);
    else if (full && beat >= 14) hat(M, t, 0.035, false);
    if (full && s === 6) hat(M, t, 0.07, true);
    if (STAB.includes(s) && !intro) stab(M, t, ch.stab, old ? 0.07 : 0.05);
    if (beat >= 14 && full) pluck(M, t, ch.stab[(s * 2 + bar) % 3] + 12, 0.035, s % 2 ? 0.3 : 0.7);
  }
}
// two-clap pickups into each new stop
[13.5, 21.5, 29.5, 37.5].forEach((b) => { clap(M, b * BEAT, 0.3); clap(M, (b + 0.25) * BEAT, 0.34); });
// "the old way" (beats 4-8): the band plays through a tinny radio, with crackle
{ const a = Math.round(4 * BEAT * SR), b = Math.round(8 * BEAT * SR);
  for (const chn of M) { let lp = 0, hp = 0; for (let i = a; i < b; i++) { lp += lpA(2300) * (chn[i] - lp); hp += lpA(650) * (lp - hp); const w = sm(i, a, a + 400) * (1 - sm(i, b - 400, b)); chn[i] = chn[i] * (1 - w) + (lp - hp) * 1.5 * w; } }
  for (let i = a; i < b; i++) { if (rnd() < 0.0012) add(M, i, noise() * 0.16); const t = i / SR; add(M, i, Math.sin(TAU * 21 * t) > 0.96 ? noise() * 0.035 : 0); } }
// the end card (beat 38 on): one held chord, half-time hits, then air
{ const t0 = 38 * BEAT; [41, 53, 60, 63, 68, 72].forEach((m, k) => { const f = mtof(m), i0 = Math.round(t0 * SR), pan = 0.3 + 0.08 * k; let lp = 0;
    for (let j = 0; i0 + j < N; j++) { const tt = j / SR; const x = Math.sin(TAU * f * tt) + 0.4 * Math.sin(TAU * f * 1.004 * tt + k) + 0.2 * Math.sin(TAU * 2 * f * tt);
      lp += lpA(2400) * (x - lp); const v = lp * sm(tt, 0, 0.05) * Math.exp(-tt / 2.4) * 0.05; add(M, i0 + j, v * (1 - pan) * 2, v * pan * 2); } });
  kick(M, t0, 0.7); bass(M, t0, 41, 0.34); clap(M, t0, 0.36);
  [40, 42].forEach((b) => { kick(M, b * BEAT, 0.5); bass(M, b * BEAT, 41, 0.24); }); [41, 43].forEach((b) => clap(M, b * BEAT, 0.3));
  kick(M, 44 * BEAT, 0.55); bass(M, 44 * BEAT, 41, 0.3); }

/* ---------------- sound design, on the picture ---------------- */
const fr = (f) => f / 30;
bell(X, 0.02, 86, 0.2); bell(X, 0.27, 86, 0.17);                        // the full-service driveway bell: ding-ding
thock(X, fr(25), 0.24, 220);                                              // "GAS" gets painted
[50, 175, 275, 375].forEach((f) => whoosh(X, fr(f), 0.34));              // whip-pans (the camera drives on)
{ // beat 8: squeegee down the glass — rubber squeal over a sheet of water
  const t0 = fr(100), i0 = Math.round(t0 * SR); let ph = 0, lp = 0, hp = 0;
  for (let j = 0; j < SR * 0.56; j++) { const tt = j / SR, k = tt / 0.5; const f = 760 + 520 * Math.sin(Math.min(1, k) * Math.PI) + 26 * Math.sin(TAU * 37 * tt); ph += TAU * f / SR;
    const env = sm(tt, 0, 0.04) * (1 - sm(tt, 0.42, 0.55)); lp += lpA(5200) * (noise() - lp); hp += lpA(1100) * (lp - hp);
    const v = (Math.sin(ph) + 0.35 * Math.sin(2 * ph)) * 0.07 * env + (lp - hp) * 0.22 * env; const p = 0.35 + 0.3 * k; add(X, i0 + j, v * (1 - p) * 2, v * p * 2); } }
[0, 0.07, 0.13, 0.18, 0.23].forEach((o, k) => tick(X, fr(42 + 63) + o, 0.05, 1500 + k * 160, 0.3 + k * 0.1));   // the new headline lands
thock(X, fr(42 + 95), 0.26, 190);                                         // the promise gets slapped on the board
[18, 44, 70].forEach((f, k) => tick(X, fr(167 + f), 0.08, 1200 + k * 150, 0.25));                                  // step plates
blip(X, fr(167 + 33), 0.13); blip(X, fr(167 + 58), 0.13);                 // taps
for (let k = 1; k <= 19; k++) tick(X, fr(167 + 20) + k * (63 / 30 / 19), 0.028, 2400 + k * 40, 0.3);               // the meter runs
thock(X, fr(167 + 83), 0.3, 150); bell(X, fr(167 + 83) + 0.02, 86, 0.16); bell(X, fr(167 + 83) + 0.26, 86, 0.13); // booked: ding-ding
pop(X, fr(167 + 95), 0.16);                                               // the pin
thock(X, fr(267 + 20), 0.34, 120);                                        // the pin lands
[60, 63, 65, 68, 70, 72, 75, 77, 80, 82, 84, 87, 89].forEach((m, k) => pluck(X, fr(267 + 21) + k * 0.07, m, 0.07, 0.75));   // 13 counties light up
[57, 66, 76].forEach((f) => thock(X, fr(267 + f), 0.2, 260)); tick(X, fr(267 + 73), 0.1, 3000, 0.25);            // signs slot onto the post
for (let k = 0; k < 16; k++) tick(X, fr(367 + 19) + k * 0.034, 0.03, 1800 + (k % 4) * 90, 0.6);                    // prices roll up
thock(X, fr(367 + 45), 0.24, 230);                                        // the WashClub column switches on
for (let k = 0; k < 14; k++) tick(X, fr(367 + 58) + k * 0.036, 0.034, 2600 - k * 60, 0.75);                        // and drops
tick(X, fr(367 + 50), 0.07, 1400, 0.5);
whoosh(X, fr(475), 0.42, 0.34, 0.75, 250, 3800);                          // up through the cloud
bell(X, fr(466 + 13), 77, 0.13, 0.7); bell(X, fr(466 + 13) + 0.03, 84, 0.1, 0.7);   // the logo lands
[0, 0.06, 0.11, 0.17, 0.22, 0.3].forEach((o, k) => tick(X, fr(466 + 19) + o, 0.045, 1500 + k * 140, 0.5));
[34, 40, 43, 45].forEach((f, k) => tick(X, fr(466 + f), 0.07, 1300 + k * 120, 0.5));

/* ---------------- master ---------------- */
const L = new Float32Array(N), R = new Float32Array(N); let peak = 0;
for (let i = 0; i < N; i++) { const t = i / SR, fo = 1 - sm(t, DUR - 0.5, DUR);
  L[i] = Math.tanh((M[0][i] + X[0][i]) * 1.5 * fo); R[i] = Math.tanh((M[1][i] + X[1][i]) * 1.5 * fo); peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i])); }
const k = 0.63 / peak, buf = Buffer.alloc(44 + N * 4);   // lands about -14 LUFS with the true peak under -3 dBFS
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(L[i] * k * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(R[i] * k * 32767), 46 + i * 4); }
fs.writeFileSync(process.argv[2], buf); console.log('wrote', process.argv[2], 'seconds', (N / SR).toFixed(3), 'pre-normalize peak', peak.toFixed(3));
