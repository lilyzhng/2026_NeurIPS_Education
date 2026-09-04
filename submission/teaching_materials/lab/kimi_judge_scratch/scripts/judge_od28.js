const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const EVID = path.join(__dirname, '..', 'evidence');

async function judgeArm(name, url) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const consoleMsgs = [];
  const pageErrors = [];
  page.on('console', m => { if (['error','warning'].includes(m.type())) consoleMsgs.push(`${m.type()}: ${m.text().slice(0,200)}`); });
  page.on('pageerror', e => pageErrors.push(String(e).slice(0, 300)));

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(EVID, `${name}_od28_0_initial.png`), fullPage: false });

  const out = { consoleMsgs, pageErrors, components: {} };

  // --- What actually rendered? ---
  out.components.render = await page.evaluate(() => {
    const tc = document.getElementById('trading-chart');
    const ac = document.getElementById('accident-chart');
    const tip = document.getElementById('tooltip');
    return {
      title: document.querySelector('h1')?.innerText || null,
      tradingChildren: tc ? tc.children.length : null,
      accidentChildren: ac ? ac.children.length : null,
      svgCount: document.querySelectorAll('svg').length,
      canvasCount: document.querySelectorAll('canvas').length,
      tooltipExists: !!tip,
      bodyTextLen: document.body.innerText.length,
      bodyTextStart: document.body.innerText.slice(0, 150),
    };
  });

  // --- Hover over chart regions: tooltip appears? (brief: interactive charts, x2) ---
  out.components.hover = {};
  for (const id of ['trading-chart', 'accident-chart']) {
    const el = await page.$(`#${id}`);
    if (!el) { out.components.hover[id] = 'container missing'; continue; }
    const box = await el.boundingBox();
    if (!box) { out.components.hover[id] = 'no bounding box'; continue; }
    const tipBefore = await page.evaluate(() => { const t = document.getElementById('tooltip'); return t ? { display: getComputedStyle(t).display, text: t.textContent } : null; });
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 5 });
    await page.waitForTimeout(300);
    const tipAfter = await page.evaluate(() => { const t = document.getElementById('tooltip'); return t ? { display: getComputedStyle(t).display, text: t.textContent } : null; });
    out.components.hover[id] = { tipBefore, tipAfter, appeared: JSON.stringify(tipBefore) !== JSON.stringify(tipAfter) };
  }

  // --- Click anywhere on chart containers: any change? ---
  out.components.click = {};
  for (const id of ['trading-chart', 'accident-chart']) {
    const el = await page.$(`#${id}`);
    if (!el) { out.components.click[id] = 'missing'; continue; }
    const bodyBefore = await page.evaluate(() => document.body.innerHTML.length);
    await el.click().catch(e => out.components.click[id] = 'click err ' + e);
    await page.waitForTimeout(300);
    const bodyAfter = await page.evaluate(() => document.body.innerHTML.length);
    if (!out.components.click[id]) out.components.click[id] = { bodyChanged: bodyBefore !== bodyAfter };
  }

  out.externalResources = await page.evaluate(() => {
    const urls = [];
    document.querySelectorAll('img[src], script[src], link[href]').forEach(el => {
      const u = el.src || el.href;
      if (u && /^https?:\/\//.test(u)) urls.push(u);
    });
    return urls;
  });
  out.hasD3 = await page.evaluate(() => typeof window.d3 !== 'undefined');

  fs.writeFileSync(path.join(EVID, `${name}_od28.json`), JSON.stringify(out, null, 2));
  await browser.close();
  return out;
}

(async () => {
  for (const [name, url] of [
    ['vanilla', 'http://127.0.0.1:8901/radar/vanilla_frontend_od28.html'],
    ['dflash', 'http://127.0.0.1:8901/radar/dflash_frontend_od28.html'],
  ]) {
    const o = await judgeArm(name, url);
    console.log(`=== ${name.toUpperCase()} ===`);
    console.log('console:', JSON.stringify(o.consoleMsgs));
    console.log('pageErrors:', JSON.stringify(o.pageErrors));
    console.log('render:', JSON.stringify(o.components.render));
    console.log('hover:', JSON.stringify(o.components.hover));
    console.log('click:', JSON.stringify(o.components.click));
    console.log('external:', JSON.stringify(o.externalResources), 'hasD3:', o.hasD3);
  }
})();
