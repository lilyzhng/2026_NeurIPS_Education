const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const results = {};

  // ---------- VANILLA ----------
  {
    const page = await browser.newPage();
    const consoleMsgs = [];
    page.on('console', m => { if (m.type() === 'error') consoleMsgs.push(m.text()); });
    page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));
    await page.goto('http://127.0.0.1:8901/radar/vanilla_frontend_od5.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);

    const snap = {};

    // 1. Nav link "About" click
    const beforeNav = await page.evaluate(() => ({ url: location.href, scrollY: window.scrollY, bodyChanged: document.body.innerHTML.length }));
    await page.click('nav a:has-text("About")');
    await page.waitForTimeout(300);
    const afterNav = await page.evaluate(() => ({ url: location.href, scrollY: window.scrollY }));
    snap.navAbout = { before: beforeNav, after: afterNav };

    // 2. Get a Quote CTA button
    const beforeQuote = await page.evaluate(() => ({ url: location.href, scrollY: window.scrollY }));
    await page.click('.cta-button');
    await page.waitForTimeout(300);
    const afterQuote = await page.evaluate(() => ({ url: location.href, scrollY: window.scrollY }));
    snap.quoteBtn = { before: beforeQuote, after: afterQuote };

    // 3. CTA form: type + submit
    await page.fill('.cta input[type="text"]', 'Jane Doe');
    await page.fill('.cta input[type="email"]', 'jane@example.com');
    const beforeForm = await page.evaluate(() => ({ url: location.href, nameVal: document.querySelector('.cta input[type="text"]').value }));
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'load', timeout: 3000 }).catch(() => null),
      page.click('.cta button[type="submit"]'),
    ]);
    await page.waitForTimeout(300);
    const afterForm = await page.evaluate(() => ({ url: location.href, nameVal: document.querySelector('.cta input[type="text"]').value, bodyText: document.body.innerText.includes('Thank') }));
    snap.ctaForm = { before: beforeForm, after: afterForm };

    // 4. Footer social link
    await page.goto('http://127.0.0.1:8901/radar/vanilla_frontend_od5.html', { waitUntil: 'load' });
    const beforeSocial = await page.evaluate(() => location.href);
    await page.click('footer .socials a:has-text("Facebook")');
    await page.waitForTimeout(300);
    const afterSocial = await page.evaluate(() => location.href);
    snap.social = { before: beforeSocial, after: afterSocial };

    results.vanilla = { consoleMsgs, snap };
    fs.writeFileSync('results/od5_vanilla_snapshot.json', JSON.stringify(snap, null, 2));
    await page.close();
  }

  // ---------- DFLASH ----------
  {
    const page = await browser.newPage();
    const consoleMsgs = [];
    const dialogs = [];
    page.on('console', m => { if (m.type() === 'error') consoleMsgs.push(m.text()); });
    page.on('pageerror', e => consoleMsgs.push('pageerror: ' + e.message));
    page.on('dialog', async d => { dialogs.push(d.message()); await d.accept(); });
    await page.goto('http://127.0.0.1:8901/radar/dflash_frontend_od5.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);

    const snap = {};

    // helper: check which section is in viewport top
    const visibleSection = () => page.evaluate(() => {
      const ids = ['benefits', 'how-it-works', 'plans', 'testimonials', 'contact'];
      for (const id of ids) {
        const el = document.getElementById(id);
        const r = el.getBoundingClientRect();
        if (r.top <= 120 && r.bottom > 120) return id;
      }
      return 'none';
    });

    // 1. Nav "Our Plans"
    const beforeNav1 = await visibleSection();
    await page.click('nav a[href="#plans"]');
    await page.waitForTimeout(400);
    const afterNav1 = await visibleSection();
    snap.navPlans = { before: beforeNav1, after: afterNav1 };

    // 2. Nav back to "Why Choose Us" (#benefits)
    await page.click('nav a[href="#benefits"]');
    await page.waitForTimeout(400);
    snap.navBenefits = { after: await visibleSection() };

    // 3. Get a Quote button -> #contact
    const beforeQuote = await visibleSection();
    await page.click('.hero .btn');
    await page.waitForTimeout(400);
    const afterQuote = await visibleSection();
    const quoteUrl = await page.evaluate(() => location.href);
    snap.quoteBtn = { before: beforeQuote, after: afterQuote, url: quoteUrl };

    // 4. Contact form: fill + submit -> alert
    await page.fill('#name', 'John Smith');
    await page.fill('#email', 'john@example.com');
    await page.fill('#phone', '555-1234');
    await page.fill('#message', 'I want a quote.');
    await page.click('.contact .btn');
    await page.waitForTimeout(400);
    snap.contactForm = { dialogsSeen: dialogs, nameValAfter: await page.evaluate(() => document.getElementById('name').value) };

    results.dflash = { consoleMsgs, dialogs, snap };
    fs.writeFileSync('results/od5_dflash_snapshot.json', JSON.stringify(snap, null, 2));
    await page.close();
  }

  fs.writeFileSync('results/od5_console.json', JSON.stringify({ vanilla: results.vanilla.consoleMsgs, dflash: results.dflash.consoleMsgs }, null, 2));
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
