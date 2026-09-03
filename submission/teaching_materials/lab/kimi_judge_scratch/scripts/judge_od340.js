const { chromium } = require('playwright');
const fs = require('fs');

const OUT = __dirname + '/../evidence_od340';
fs.mkdirSync(OUT, { recursive: true });

async function judge(name, url) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  const consoleMsgs = [];
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) consoleMsgs.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));
  const failedReqs = [];
  page.on('requestfailed', r => failedReqs.push(r.url() + ' :: ' + (r.failure() && r.failure().errorText)));

  await page.goto(url, { waitUntil: 'networkidle' }).catch(e => consoleMsgs.push('goto: ' + e.message));
  await page.waitForTimeout(800);

  const r = { name, consoleMsgs, failedReqs };

  // State before hover
  r.before = await page.evaluate(() => {
    const card = document.querySelector('.card');
    const faces = [...document.querySelectorAll('.face')];
    const cs = getComputedStyle(card);
    return {
      cardTransform: cs.transform,
      cardPosition: cs.position,
      cardRect: card.getBoundingClientRect().toJSON(),
      faces: faces.map(f => {
        const fc = getComputedStyle(f);
        return {
          cls: f.className, transform: fc.transform, position: fc.position,
          backface: fc.backfaceVisibility,
          rect: f.getBoundingClientRect().toJSON(),
          bg: fc.backgroundImage.slice(0, 80),
          imgCount: f.querySelectorAll('img').length,
          imgComplete: [...f.querySelectorAll('img')].map(i => ({ src: i.src, complete: i.complete, nw: i.naturalWidth })),
        };
      }),
      bodyText: document.body.innerText.slice(0, 200),
    };
  });

  await page.screenshot({ path: OUT + '/' + name + '_before.png' });

  // Hover the card
  await page.hover('.card');
  await page.waitForTimeout(300); // mid-transition
  r.midHover = await page.evaluate(() => getComputedStyle(document.querySelector('.card')).transform);
  await page.screenshot({ path: OUT + '/' + name + '_mid.png' });
  await page.waitForTimeout(700); // after transition
  r.after = await page.evaluate(() => {
    const card = document.querySelector('.card');
    return {
      cardTransform: getComputedStyle(card).transform,
      facesVisible: [...document.querySelectorAll('.face')].map(f => {
        const rect = f.getBoundingClientRect();
        return { cls: f.className, rect: rect.toJSON() };
      }),
    };
  });
  await page.screenshot({ path: OUT + '/' + name + '_hover.png' });

  // Unhover
  await page.mouse.move(50, 50);
  await page.waitForTimeout(800);
  r.unhover = await page.evaluate(() => getComputedStyle(document.querySelector('.card')).transform);

  await browser.close();
  return r;
}

(async () => {
  const results = [];
  results.push(await judge('vanilla', 'http://127.0.0.1:8901/radar/vanilla_frontend_od340.html'));
  results.push(await judge('dflash', 'http://127.0.0.1:8901/radar/dflash_frontend_od340.html'));
  fs.writeFileSync(OUT + '/results.json', JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})();
