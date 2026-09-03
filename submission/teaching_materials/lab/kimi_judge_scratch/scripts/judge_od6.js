const { chromium } = require('playwright');
const fs = require('fs');

const arms = {
  vanilla: 'http://127.0.0.1:8901/radar/vanilla_frontend_od6.html',
  dflash: 'http://127.0.0.1:8901/radar/dflash_frontend_od6.html',
};

async function state(page) {
  return await page.evaluate(() => ({
    hash: location.hash,
    scrollY: Math.round(window.scrollY),
  }));
}

async function tryClick(page, selector, label, rec, wait = 600) {
  const before = await state(page);
  try {
    await page.click(selector, { timeout: 5000 });
    await page.waitForTimeout(wait);
    const after = await state(page);
    rec.tests[label] = { before, after, changed: before.hash !== after.hash || before.scrollY !== after.scrollY };
  } catch (e) {
    const intercept = /<[^>]+>[^<]*intercepts pointer events/.exec(e.message);
    rec.tests[label] = { clickFailed: true, reason: intercept ? intercept[0] : e.message.split('\n')[0] };
  }
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const [arm, url] of Object.entries(arms)) {
    const page = await browser.newPage();
    const consoleMsgs = [];
    page.on('console', m => { if (['error','warning'].includes(m.type())) consoleMsgs.push(m.type()+': '+m.text()); });
    page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));
    const failedReqs = [];
    page.on('requestfailed', r => failedReqs.push(r.url()));
    const extReqs = [];
    page.on('request', r => { if (/^https?:\/\//.test(r.url()) && !r.url().includes('127.0.0.1')) extReqs.push(r.url()); });
    await page.goto(url, { waitUntil: 'networkidle' }).catch(()=>{});
    await page.waitForTimeout(500);

    const rec = { console: consoleMsgs, failedReqs, extReqs, tests: {} };

    rec.sections = await page.evaluate(() => ({
      home: !!document.getElementById('home'),
      products: !!document.getElementById('products'),
      about: !!document.getElementById('about'),
      contact: !!document.getElementById('contact'),
      cta: !!document.getElementById('cta'),
    }));

    // Nav: Products (from top)
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForTimeout(200);
    await tryClick(page, '.nav-links a[href="#products"]', 'nav_products', rec);

    // Nav: About
    await tryClick(page, '.nav-links a[href="#about"]', 'nav_about', rec);

    // Nav: Contact
    await tryClick(page, '.nav-links a[href="#contact"]', 'nav_contact', rec);

    // Nav: Home (come back after being at contact)
    await tryClick(page, '.nav-links a[href="#home"]', 'nav_home', rec);

    // Hero: Shop Now (from top)
    await page.evaluate(() => { window.scrollTo(0,0); });
    await page.waitForTimeout(300);
    await tryClick(page, '.hero button', 'shop_now', rec);

    // Add to Cart (first card) — fresh page load at top, per rule 6
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await tryClick(page, '.product-card button', 'add_to_cart', rec);
    rec.tests.add_to_cart.domCheck = await page.evaluate(() => ({
      cartEls: document.querySelectorAll('[class*="cart" i], [id*="cart" i]').length,
      buttons: document.querySelectorAll('button').length,
    }));

    // Subscribe Now — scroll to top first so any scroll change is visible
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForTimeout(200);
    await tryClick(page, '.cta button', 'subscribe', rec);
    rec.tests.subscribe.subDom = await page.evaluate(() => ({
      inputs: document.querySelectorAll('input').length,
      forms: document.querySelectorAll('form').length,
    }));

    // Footer link (first) — scroll into view then click
    const flink = await page.$('footer a');
    if (flink) {
      const href = await flink.getAttribute('href');
      await flink.scrollIntoViewIfNeeded();
      const before = await state(page);
      try {
        await flink.click({ timeout: 5000 });
        await page.waitForTimeout(400);
        const after = await state(page);
        rec.tests.footer_link = { href, before, after, changed: before.hash !== after.hash || before.scrollY !== after.scrollY };
      } catch (e) {
        rec.tests.footer_link = { href, clickFailed: true, reason: e.message.split('\n')[0] };
      }
    }

    // Hover: product card transform
    const card = await page.$('.product-card');
    await card.scrollIntoViewIfNeeded();
    const tBefore = await card.evaluate(el => getComputedStyle(el).transform);
    await card.hover();
    await page.waitForTimeout(500);
    const tAfter = await card.evaluate(el => getComputedStyle(el).transform);
    rec.tests.card_hover = { tBefore, tAfter, changed: tBefore !== tAfter };

    rec.inputsCount = await page.evaluate(() => document.querySelectorAll('input, textarea').length);

    out[arm] = rec;
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(__dirname + '/../results/od6_evidence.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
})();
