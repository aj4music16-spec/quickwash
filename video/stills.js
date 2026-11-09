// Usage: node stills.js out_dir t1 t2 ...  — capture single frames for review
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, ...times] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await pg.goto('file://' + path.resolve(__dirname, 'index.html') + '?render');
  await pg.waitForFunction(() => window.__ready);
  for (const t of times) {
    await pg.evaluate(t => seek(t), +t);
    await pg.screenshot({ path: `${out}/t${(+t).toFixed(2)}.jpg`, quality: 80 });
  }
  await b.close();
})();
