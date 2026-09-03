const { chromium } = require('playwright');
const fs = require('fs');

const BASE = 'http://127.0.0.1:8901/radar/';
const arms = ['vanilla', 'dflash'];

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const arm of arms) {
    const url = `${BASE}${arm}_frontend_od9.html`;
    const page = await browser.newPage();
    const consoleMsgs = [];
    const pageErrors = [];
    const dialogs = [];
    page.on('console', m => { if (m.type() === 'error') consoleMsgs.push(m.text()); });
    page.on('pageerror', e => pageErrors.push(String(e)));
    page.on('dialog', async d => { dialogs.push(d.message()); await d.accept(); });

    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(500);

    const res = { consoleMsgs, pageErrors, dialogs, interactions: {} };

    // DOM snapshot before
    res.interactions.before = await page.evaluate(() => ({
      bodyClasses: document.body.className,
      hash: location.hash,
      scrollY: window.scrollY,
    }));

    // 1. Hero button hover: computed background before/after
    const btn = page.locator('.hero button');
    res.interactions.btnHoverBefore = await btn.evaluate(el => getComputedStyle(el).backgroundColor + ' | ' + getComputedStyle(el).backgroundImage);
    await btn.hover();
    await page.waitForTimeout(400);
    res.interactions.btnHoverAfter = await btn.evaluate(el => getComputedStyle(el).backgroundColor + ' | ' + getComputedStyle(el).backgroundImage);

    // 2. Hero button click
    const btnText = await btn.innerText();
    res.interactions.btnText = btnText;
    const hasOnclick = await btn.evaluate(el => el.getAttribute('onclick'));
    res.interactions.btnOnclickAttr = hasOnclick;
    await btn.click();
    await page.waitForTimeout(400);
    res.interactions.afterBtnClick = await page.evaluate(() => ({
      hash: location.hash, scrollY: window.scrollY,
      bodyHTMLlen: document.body.innerHTML.length,
    }));
    res.interactions.dialogsAfterBtnClick = dialogs.slice();

    // 3. Footer links
    const links = await page.locator('footer a').all();
    res.interactions.footerLinks = [];
    for (const link of links) {
      const text = await link.innerText();
      const href = await link.getAttribute('href');
      // scroll down first so a scroll-to-top is detectable
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(200);
      const beforeState = await page.evaluate(() => ({ hash: location.hash, scrollY: window.scrollY }));
      await link.click();
      await page.waitForTimeout(300);
      const afterState = await page.evaluate(() => ({ hash: location.hash, scrollY: window.scrollY }));
      res.interactions.footerLinks.push({ text, href, beforeState, afterState, dialogs: dialogs.slice() });
    }

    // 4. Check for any inputs/forms
    res.interactions.inputCount = await page.locator('input, textarea, form, select').count();

    out[arm] = res;
    await page.close();
  }
  await browser.close();
  fs.mkdirSync('evidence', { recursive: true });
  fs.writeFileSync('evidence/od9.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
})();
