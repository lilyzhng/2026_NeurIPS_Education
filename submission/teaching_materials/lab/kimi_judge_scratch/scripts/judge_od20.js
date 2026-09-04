const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const EVID = path.join(__dirname, '..', 'evidence');

async function judgeArm(name, url) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const consoleMsgs = [];
  const pageErrors = [];
  page.on('console', m => { if (['error','warning'].includes(m.type())) consoleMsgs.push(`${m.type()}: ${m.text()}`); });
  page.on('pageerror', e => pageErrors.push(String(e)));

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(EVID, `${name}_od20_0_initial.png`), fullPage: true });

  const out = { consoleMsgs, pageErrors, components: {} };

  // --- Did each canvas actually render (non-uniform pixels)? ---
  out.components.canvasRender = await page.evaluate(() => {
    const res = {};
    for (const id of ['lineChart', 'barChart']) {
      const c = document.getElementById(id);
      if (!c) { res[id] = { exists: false }; continue; }
      const ctx = c.getContext('2d');
      const d = ctx.getImageData(0, 0, c.width, c.height).data;
      let distinct = new Set();
      for (let i = 0; i < d.length; i += 4013 * 4) distinct.add(`${d[i]},${d[i+1]},${d[i+2]},${d[i+3]}`);
      res[id] = { exists: true, w: c.width, h: c.height, distinctSampledColors: distinct.size, drawn: distinct.size > 1 };
    }
    return res;
  });

  // --- Tooltip presence in DOM ---
  out.components.tooltipsInDom = await page.evaluate(() => {
    return [...document.querySelectorAll('.tooltip, [id*="tooltip"], [id*="Tooltip"]')].map(t => ({ id: t.id, cls: t.className, display: getComputedStyle(t).display }));
  });

  // --- Hover over canvases: does a tooltip appear / anything change? (brief: interactive, x2) ---
  out.components.hover = {};
  for (const id of ['lineChart', 'barChart']) {
    const el = await page.$(`#${id}`);
    if (!el) { out.components.hover[id] = 'missing'; continue; }
    await el.scrollIntoViewIfNeeded();
    const box = await el.boundingBox();
    const tipBefore = await page.evaluate(() => [...document.querySelectorAll('.tooltip, [id*="tooltip"], [id*="Tooltip"]')].map(t => ({ id: t.id, display: getComputedStyle(t).display, text: t.textContent })));
    // sweep mouse across several points of the canvas
    for (const fx of [0.25, 0.5, 0.75]) {
      for (const fy of [0.3, 0.5, 0.7]) {
        await page.mouse.move(box.x + box.width * fx, box.y + box.height * fy, { steps: 4 });
        await page.waitForTimeout(120);
      }
    }
    await page.waitForTimeout(300);
    const tipAfter = await page.evaluate(() => [...document.querySelectorAll('.tooltip, [id*="tooltip"], [id*="Tooltip"]')].map(t => ({ id: t.id, display: getComputedStyle(t).display, text: t.textContent })));
    out.components.hover[id] = { tipBefore, tipAfter, appeared: JSON.stringify(tipBefore) !== JSON.stringify(tipAfter) };
  }
  await page.screenshot({ path: path.join(EVID, `${name}_od20_1_hover.png`), fullPage: true });

  // --- Any click interaction on canvases? ---
  out.components.click = {};
  for (const id of ['lineChart', 'barChart']) {
    const el = await page.$(`#${id}`);
    if (!el) { out.components.click[id] = 'missing'; continue; }
    const bodyBefore = await page.evaluate(() => document.body.innerHTML.length);
    const box = await el.boundingBox();
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(300);
    const bodyAfter = await page.evaluate(() => document.body.innerHTML.length);
    out.components.click[id] = { bodyChanged: bodyBefore !== bodyAfter };
  }

  // --- listener inventory from source check: count addEventListener in inline scripts ---
  out.listenerCount = await page.evaluate(() => {
    let n = 0;
    document.querySelectorAll('script:not([src])').forEach(s => { n += (s.textContent.match(/addEventListener/g) || []).length; });
    return n;
  });
  out.externalResources = await page.evaluate(() => {
    const urls = [];
    document.querySelectorAll('img[src], script[src], link[href]').forEach(el => {
      const u = el.src || el.href;
      if (u && /^https?:\/\//.test(u)) urls.push(u);
    });
    return urls;
  });
  out.bodyEnd = await page.evaluate(() => document.body.innerText.slice(-100));

  fs.writeFileSync(path.join(EVID, `${name}_od20.json`), JSON.stringify(out, null, 2));
  await browser.close();
  return out;
}

(async () => {
  for (const [name, url] of [
    ['vanilla', 'http://127.0.0.1:8901/radar/vanilla_frontend_od20.html'],
    ['dflash', 'http://127.0.0.1:8901/radar/dflash_frontend_od20.html'],
  ]) {
    const o = await judgeArm(name, url);
    console.log(`=== ${name.toUpperCase()} ===`);
    console.log('console:', JSON.stringify(o.consoleMsgs));
    console.log('pageErrors:', JSON.stringify(o.pageErrors));
    console.log('canvasRender:', JSON.stringify(o.components.canvasRender));
    console.log('tooltipsInDom:', JSON.stringify(o.components.tooltipsInDom));
    console.log('hover:', JSON.stringify(o.components.hover));
    console.log('click:', JSON.stringify(o.components.click));
    console.log('listenerCount:', o.listenerCount, 'external:', JSON.stringify(o.externalResources));
    console.log('bodyEnd:', JSON.stringify(o.bodyEnd));
  }
})();
