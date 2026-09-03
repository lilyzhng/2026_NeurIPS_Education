const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const EVID = path.join(__dirname, '..', 'evidence');

async function judgeArm(name, url) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const consoleMsgs = [];
  const pageErrors = [];
  const dialogs = [];
  page.on('console', m => { if (['error','warning'].includes(m.type())) consoleMsgs.push(`${m.type()}: ${m.text()}`); });
  page.on('pageerror', e => pageErrors.push(String(e)));
  page.on('dialog', async d => { dialogs.push(`${d.type()}: ${d.message()}`); await d.accept(); });

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(500);

  const out = { consoleMsgs, pageErrors, dialogs, components: {} };
  const snap = async (sel) => {
    try {
      return await page.evaluate(s => {
        const el = document.querySelector(s);
        if (!el) return null;
        return { tag: el.tagName, cls: el.className, text: el.innerText.slice(0,120),
                 html: el.outerHTML.slice(0, 300) };
      }, sel);
    } catch(e) { return 'ERR ' + e; }
  };

  const isScrolledTo = async (id) => await page.evaluate(id => {
    const el = document.querySelector(id);
    if (!el) return false;
    const r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  }, id);

  // --- Nav links ---
  const navLinks = await page.$$eval('nav a', as => as.map(a => ({ text: a.innerText, href: a.getAttribute('href') })));
  out.components.navLinks = { found: navLinks, results: [] };
  for (const nl of navLinks) {
    const before = await isScrolledTo(nl.href);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(200);
    // navigate away first if already at target: scroll to top then click another link, then this one
    await page.click(`nav a[href="${nl.href}"]`);
    await page.waitForTimeout(400);
    const after = await isScrolledTo(nl.href);
    const hash = await page.evaluate(() => location.hash);
    out.components.navLinks.results.push({ text: nl.text, href: nl.href, visibleBefore: before, visibleAfter: after, hashAfter: hash });
  }

  // --- Hero button ---
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);
  const heroBefore = await isScrolledTo('#booking');
  await page.click('.hero button');
  await page.waitForTimeout(500);
  const heroAfter = await isScrolledTo('#booking');
  const heroHash = await page.evaluate(() => location.hash);
  out.components.heroButton = { bookingVisibleBefore: heroBefore, bookingVisibleAfter: heroAfter, hashAfter: heroHash };

  // --- Booking form ---
  const formSel = await page.$('form.booking-form') ? 'form.booking-form' : '.booking-form';
  const inputs = await page.$$(`${formSel} input`);
  for (let i = 0; i < inputs.length; i++) {
    const ph = await inputs[i].getAttribute('placeholder');
    const type = await inputs[i].getAttribute('type');
    try {
      if (type === 'number') await inputs[i].fill('4');
      else await inputs[i].fill('2026-09-10');
    } catch(e) { out.components['input'+i] = 'fill failed: ' + e; }
    out.components['input_' + (ph||i)] = { type, filled: await inputs[i].inputValue() };
  }
  const selects = await page.$$(`${formSel} select`);
  for (const s of selects) {
    const opts = await s.$$eval('option', os => os.map(o => o.textContent.trim()));
    if (opts.length > 1) { await s.selectOption({ index: 1 }); }
    out.components['select'] = { options: opts, selected: await s.evaluate(el => el.value) };
  }
  // capture form outerHTML before submit
  const formBefore = await snap(formSel);
  const btnSel = `${formSel} button`;
  const btnExists = await page.$(btnSel) !== null;
  const dialogsBefore = dialogs.length;
  let bodyChanged = null;
  const bodyBefore = await page.evaluate(() => document.body.innerHTML.length);
  await page.click(btnSel);
  await page.waitForTimeout(600);
  const bodyAfter = await page.evaluate(() => document.body.innerHTML.length);
  bodyChanged = bodyBefore !== bodyAfter;
  out.components.bookingSubmit = {
    formIsRealForm: formSel.startsWith('form'),
    buttonExists: btnExists,
    formBefore,
    dialogsBeforeSubmit: dialogsBefore,
    dialogsAfterSubmit: dialogs.length,
    newDialogs: dialogs.slice(dialogsBefore),
    bodyChanged,
    hasOnsubmit: await page.evaluate(s => {
      const f = document.querySelector(s);
      return f ? (f.tagName === 'FORM' ? !!f.onsubmit || f.hasAttribute('onsubmit') : false) : null;
    }, formSel)
  };

  // --- Hover cards (features / suggestions / activities) ---
  for (const sel of ['.feature', '.suggestion', '.suggestion-card', '.activity-card']) {
    const el = await page.$(sel);
    if (!el) continue;
    await el.scrollIntoViewIfNeeded();
    const before = await page.evaluate(s => {
      const e = document.querySelector(s);
      const cs = getComputedStyle(e);
      return { transform: cs.transform };
    }, sel);
    await el.hover();
    await page.waitForTimeout(400);
    const after = await page.evaluate(s => {
      const e = document.querySelector(s);
      const cs = getComputedStyle(e);
      return { transform: cs.transform };
    }, sel);
    out.components['hover_' + sel.replace('.','')] = { before, after, changed: before.transform !== after.transform };
  }

  // --- Font Awesome icons check (vanilla has fas classes) ---
  out.faIcons = await page.evaluate(() => {
    const icons = [...document.querySelectorAll('i.fas')];
    return icons.map(i => {
      const cs = getComputedStyle(i, '::before');
      return { cls: i.className, content: cs.content, fontFamily: cs.fontFamily, visible: i.offsetWidth > 0 };
    });
  });

  // --- external resources ---
  out.externalResources = await page.evaluate(() => {
    const urls = [];
    document.querySelectorAll('img[src], script[src], link[href]').forEach(el => {
      const u = el.src || el.href;
      if (u && /^https?:\/\//.test(u)) urls.push(u);
    });
    return urls;
  });

  fs.writeFileSync(path.join(EVID, `${name}_od8.json`), JSON.stringify(out, null, 2));
  await browser.close();
  return out;
}

(async () => {
  const v = await judgeArm('vanilla', 'http://127.0.0.1:8901/radar/vanilla_frontend_od8.html');
  const d = await judgeArm('dflash', 'http://127.0.0.1:8901/radar/dflash_frontend_od8.html');
  console.log('VANILLA console/pageErrors:', JSON.stringify(v.consoleMsgs), JSON.stringify(v.pageErrors));
  console.log('VANILLA dialogs:', JSON.stringify(v.dialogs));
  console.log('VANILLA bookingSubmit:', JSON.stringify(v.components.bookingSubmit.newDialogs), 'bodyChanged:', v.components.bookingSubmit.bodyChanged);
  console.log('VANILLA nav:', JSON.stringify(v.components.navLinks.results));
  console.log('VANILLA hero:', JSON.stringify(v.components.heroButton));
  console.log('VANILLA hovers:', JSON.stringify(Object.keys(v.components).filter(k=>k.startsWith('hover_')).map(k=>({k, changed: v.components[k].changed}))));
  console.log('VANILLA faIcons:', JSON.stringify(v.faIcons));
  console.log('VANILLA external:', JSON.stringify(v.externalResources));
  console.log('---');
  console.log('DFLASH console/pageErrors:', JSON.stringify(d.consoleMsgs), JSON.stringify(d.pageErrors));
  console.log('DFLASH dialogs:', JSON.stringify(d.dialogs));
  console.log('DFLASH bookingSubmit:', JSON.stringify(d.components.bookingSubmit.newDialogs), 'bodyChanged:', d.components.bookingSubmit.bodyChanged, 'isForm:', d.components.bookingSubmit.formIsRealForm);
  console.log('DFLASH nav:', JSON.stringify(d.components.navLinks.results));
  console.log('DFLASH hero:', JSON.stringify(d.components.heroButton));
  console.log('DFLASH hovers:', JSON.stringify(Object.keys(d.components).filter(k=>k.startsWith('hover_')).map(k=>({k, changed: d.components[k].changed}))));
  console.log('DFLASH external:', JSON.stringify(d.externalResources));
})();
