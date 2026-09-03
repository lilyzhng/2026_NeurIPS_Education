const { chromium } = require('playwright');

const arms = [
  { name: 'vanilla', url: 'http://127.0.0.1:8901/radar/vanilla_frontend_od341.html' },
  { name: 'dflash', url: 'http://127.0.0.1:8901/radar/dflash_frontend_od341.html' },
];

(async () => {
  const browser = await chromium.launch();
  const report = {};

  for (const arm of arms) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }); // smartphone
    const page = await ctx.newPage();
    const consoleMsgs = [];
    page.on('console', m => { if (m.type() === 'error') consoleMsgs.push('console.error: ' + m.text()); });
    page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));

    await page.goto(arm.url, { waitUntil: 'load' });
    await page.waitForTimeout(500);

    const r = { console_errors: consoleMsgs };

    // 1. Popup visible on load?
    r.popup_visible_on_load = await page.evaluate(() => {
      const p = document.querySelector('.popup');
      if (!p) return null;
      const cs = getComputedStyle(p);
      const rect = p.getBoundingClientRect();
      return { display: cs.display, visibility: cs.visibility, opacity: cs.opacity, w: rect.width, h: rect.height };
    });
    r.before_dom = await page.evaluate(() => document.querySelector('.popup')?.outerHTML.slice(0, 600));

    // 2. Subscribe flow: type email, submit, check for confirmation / popup change
    await page.fill('input[type="email"]', 'test@example.com');
    r.email_typed = await page.evaluate(() => document.querySelector('input[type="email"]').value);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(600);
    r.after_submit = await page.evaluate(() => {
      const p = document.querySelector('.popup');
      const cs = p ? getComputedStyle(p) : null;
      return {
        popup_exists: !!p,
        popup_display: cs?.display,
        popup_visibility: cs?.visibility,
        popup_opacity: cs?.opacity,
        popup_classes: p?.className,
        body_text: document.body.innerText.trim().slice(0, 300),
      };
    });
    r.after_submit_dom = await page.evaluate(() => document.body.innerHTML.slice(0, 900));

    // 3. Reload for close-button test (popup state may already be dismissed)
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(400);
    r.before_close = await page.evaluate(() => {
      const p = document.querySelector('.popup');
      const cs = p ? getComputedStyle(p) : null;
      return { visibility: cs?.visibility, display: cs?.display, opacity: cs?.opacity };
    });
    await page.click('.close-btn');
    await page.waitForTimeout(500);
    r.after_close = await page.evaluate(() => {
      const p = document.querySelector('.popup');
      const cs = p ? getComputedStyle(p) : null;
      return { visibility: cs?.visibility, display: cs?.display, opacity: cs?.opacity, classes: p?.className };
    });

    // invalid email should be blocked by native validation
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(300);
    await page.fill('input[type="email"]', 'notanemail');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(400);
    r.invalid_email = await page.evaluate(() => {
      const inp = document.querySelector('input[type="email"]');
      const p = document.querySelector('.popup');
      const cs = p ? getComputedStyle(p) : null;
      return { valid: inp.checkValidity(), popup_visibility: cs?.visibility, popup_display: cs?.display };
    });

    report[arm.name] = r;
    await ctx.close();
  }

  console.log(JSON.stringify(report, null, 2));
  await browser.close();
})();
