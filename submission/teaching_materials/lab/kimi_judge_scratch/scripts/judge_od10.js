const { chromium } = require('playwright');

async function judgeArm(url, label) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const consoleMsgs = [];
  page.on('console', m => { if (m.type() === 'error') consoleMsgs.push('console.error: ' + m.text()); });
  page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));

  const out = { url, consoleMsgs, components: {} };

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(500);

  // --- Component 1: CTA button ---
  // vanilla: <a href="#contact" class="cta-button">, dflash: <button class="button">
  const cta = page.locator('.cta-button, .button').first();
  const ctaBefore = {
    tag: await cta.evaluate(el => el.tagName),
    href: await cta.evaluate(el => el.getAttribute('href')),
    scrollY: await page.evaluate(() => window.scrollY),
    contactInView: await page.evaluate(() => {
      const el = document.querySelector('#contact, .contact');
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight && r.bottom > 0;
    })
  };
  // hover transform check on CTA
  const ctaTransformBefore = await cta.evaluate(el => getComputedStyle(el).transform);
  await cta.hover();
  await page.waitForTimeout(400);
  const ctaTransformAfter = await cta.evaluate(el => getComputedStyle(el).transform);
  await cta.click();
  await page.waitForTimeout(1200);
  const ctaAfter = {
    scrollY: await page.evaluate(() => window.scrollY),
    contactInView: await page.evaluate(() => {
      const el = document.querySelector('#contact, .contact');
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight && r.bottom > 0;
    }),
    hash: await page.evaluate(() => location.hash)
  };
  out.components.cta = { before: ctaBefore, after: ctaAfter, hoverTransform: { before: ctaTransformBefore, after: ctaTransformAfter } };

  // --- Component 2: work card hover lift ---
  const card = page.locator('.work-card, .work .card').first();
  await card.scrollIntoViewIfNeeded();
  const cardTransformBefore = await card.evaluate(el => getComputedStyle(el).transform);
  await card.hover();
  await page.waitForTimeout(500);
  const cardTransformAfter = await card.evaluate(el => getComputedStyle(el).transform);
  out.components.workCardHover = { before: cardTransformBefore, after: cardTransformAfter };

  // --- Component 3: contact form submit ---
  const form = page.locator('form').first();
  await form.scrollIntoViewIfNeeded();
  await page.evaluate(() => { window.__alive = 'marker123'; });
  await page.fill('input[type="text"]', 'Test User');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('textarea', 'Hello, I love your films.');
  const urlBefore = page.url();
  await page.locator('form button[type="submit"]').click();
  await page.waitForTimeout(1500);
  const after = {
    url: page.url(),
    urlBefore,
    markerSurvived: await page.evaluate(() => window.__alive === 'marker123'),
    nameValue: await page.evaluate(() => { const i = document.querySelector('input[type="text"]'); return i ? i.value : null; }),
    confirmationText: await page.evaluate(() => {
      const body = document.body.innerText;
      return /thank|sent|success|received|confirm/i.test(body);
    }),
    newDomNodes: await page.evaluate(() => document.querySelectorAll('.success, .confirmation, [class*="thank"], [class*="message-sent"]').length)
  };
  out.components.contactForm = after;

  // screenshot for the record
  await page.screenshot({ path: `shot_${label}.png`, fullPage: true });
  await browser.close();
  return out;
}

(async () => {
  const vanilla = await judgeArm('http://127.0.0.1:8901/radar/vanilla_frontend_od10.html', 'vanilla_od10');
  const dflash = await judgeArm('http://127.0.0.1:8901/radar/dflash_frontend_od10.html', 'dflash_od10');
  console.log(JSON.stringify({ vanilla, dflash }, null, 2));
})();
