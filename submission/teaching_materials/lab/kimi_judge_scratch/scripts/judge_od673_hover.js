const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8901/vanilla_raw.html');
  await page.click('.calendar-button');
  await page.waitForTimeout(400);
  const cells = await page.$$('.calendar-day');
  // find a plain day (no today class)
  for (const c of cells) {
    const cls = (await c.getAttribute('class')) || '';
    if (!cls.includes('today')) {
      const before = await c.evaluate(el => getComputedStyle(el).backgroundColor);
      await c.hover();
      await page.waitForTimeout(300);
      const after = await c.evaluate(el => getComputedStyle(el).backgroundColor);
      console.log(JSON.stringify({ text: (await c.textContent()).trim(), before, after, changed: before !== after }));
      break;
    }
  }
  await browser.close();
})();
