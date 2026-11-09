// Renders index.html to an MP4 by stepping the timeline frame-by-frame in
// headless Chromium (Playwright) and piping each frame into ffmpeg.
// Usage: node render.js [out.mp4] [--fps 30]
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const out = path.resolve(args.find(a => a.endsWith('.mp4')) || path.join(__dirname, '..', 'dist', 'quickwash-the-reset.mp4'));
const fps = +(args[args.indexOf('--fps') + 1] || 30) || 30;
fs.mkdirSync(path.dirname(out), { recursive: true });

(async () => {
  const wav = path.join(path.dirname(out), 'soundtrack.wav');
  execFileSync('node', [path.join(__dirname, 'audio.js'), wav], { stdio: 'inherit' });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?render');
  await page.waitForFunction(() => window.__ready === true);
  const duration = await page.evaluate(() => window.DURATION);
  const total = Math.round(duration * fps);

  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-i', wav,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });

  const t0 = Date.now();
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.seek(t), f / fps);
    const jpg = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % fps === 0) process.stdout.write(`\r  rendering ${(f / fps).toFixed(0)}s / ${duration}s  (${((Date.now() - t0) / 1000).toFixed(0)}s elapsed)`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log(`\nwrote ${out}`);
})();
