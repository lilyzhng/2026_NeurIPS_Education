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
  await page.screenshot({ path: path.join(EVID, `${name}_od11_0_initial.png`) });

  const out = { consoleMsgs, pageErrors, dialogs, components: {} };

  // --- Sidebar nav links ---
  const navLinks = await page.$$eval('.sidebar a, .sidebar nav a', as => as.map(a => ({ text: a.innerText.trim(), href: a.getAttribute('href') })));
  out.components.navLinks = { found: navLinks, results: [] };
  for (let i = 0; i < navLinks.length; i++) {
    const hashBefore = await page.evaluate(() => location.hash);
    const bodyBefore = await page.evaluate(() => document.body.innerHTML.length);
    await page.click(`.sidebar a >> nth=${i}`).catch(e => out.components.navLinks.results.push({ i, err: String(e) }));
    await page.waitForTimeout(300);
    const hashAfter = await page.evaluate(() => location.hash);
    const bodyAfter = await page.evaluate(() => document.body.innerHTML.length);
    out.components.navLinks.results.push({ text: navLinks[i].text, href: navLinks[i].href, hashBefore, hashAfter, bodyChanged: bodyBefore !== bodyAfter });
  }

  // --- Search input: type + Enter (no submit button exists) ---
  const searchSel = '.main-header input';
  const searchExists = await page.$(searchSel) !== null;
  let searchRes = { exists: searchExists };
  if (searchExists) {
    const cardsBefore = await page.$$eval('.playlist-card', els => els.map(e => e.querySelector('h3')?.innerText));
    await page.fill(searchSel, 'workout');
    await page.press(searchSel, 'Enter');
    await page.waitForTimeout(400);
    const cardsAfter = await page.$$eval('.playlist-card', els => els.map(e => e.querySelector('h3')?.innerText));
    const bodyChanged = cardsBefore.join() !== cardsAfter.join();
    searchRes = { exists: true, typed: await page.inputValue(searchSel), cardsBefore, cardsAfter, contentChanged: bodyChanged, newDialogs: dialogs.length };
  }
  out.components.search = searchRes;

  // --- Play buttons ---
  const playCount = await page.$$eval('.playlist-card button', bs => bs.length);
  let playRes = { count: playCount, results: [] };
  for (let i = 0; i < playCount; i++) {
    const bodyBefore = await page.evaluate(() => document.body.innerHTML.length);
    const dlgBefore = dialogs.length;
    await page.click(`.playlist-card button >> nth=${i}`);
    await page.waitForTimeout(300);
    const bodyAfter = await page.evaluate(() => document.body.innerHTML.length);
    playRes.results.push({ i, bodyChanged: bodyBefore !== bodyAfter, newDialogs: dialogs.length - dlgBefore });
  }
  out.components.playButtons = playRes;

  // --- Create playlist flow (brief, x2): type name, click button ---
  const formSel = (await page.$('.playlist-creation')) ? '.playlist-creation' : '.playlist-form';
  const cardsBefore = await page.$$eval('.playlist-card', els => els.length);
  const textBefore = await page.evaluate(() => document.body.innerText);
  await page.fill(`${formSel} input`, 'My Test Playlist');
  const dlgBefore = dialogs.length;
  await page.click(`${formSel} button`);
  await page.waitForTimeout(500);
  const cardsAfter = await page.$$eval('.playlist-card', els => els.length);
  const textAfter = await page.evaluate(() => document.body.innerText);
  out.components.createPlaylist = {
    formSel,
    typedValue: await page.inputValue(`${formSel} input`).catch(() => '(cleared)'),
    cardsBefore, cardsAfter,
    newCardAppeared: cardsAfter > cardsBefore,
    newDialogs: dialogs.slice(dlgBefore),
    newTextAppeared: textAfter !== textBefore,
    textDelta: textAfter.length - textBefore.length
  };
  await page.screenshot({ path: path.join(EVID, `${name}_od11_1_after_create.png`) });

  // --- Hover feedback: sidebar link + play button ---
  const hoverTests = [];
  for (const sel of ['.sidebar a', '.playlist-card button']) {
    const el = await page.$(sel);
    if (!el) continue;
    const before = await page.evaluate(s => { const cs = getComputedStyle(document.querySelector(s)); return { bg: cs.backgroundColor, color: cs.color }; }, sel);
    await el.hover();
    await page.waitForTimeout(350);
    const after = await page.evaluate(s => { const cs = getComputedStyle(document.querySelector(s)); return { bg: cs.backgroundColor, color: cs.color }; }, sel);
    hoverTests.push({ sel, before, after, changed: before.bg !== after.bg || before.color !== after.color });
  }
  out.components.hover = hoverTests;

  // --- external resources ---
  out.externalResources = await page.evaluate(() => {
    const urls = [];
    document.querySelectorAll('img[src], script[src], link[href]').forEach(el => {
      const u = el.src || el.href;
      if (u && /^https?:\/\//.test(u)) urls.push(u);
    });
    return urls;
  });
  // image load status
  out.imageStatus = await page.evaluate(() => [...document.querySelectorAll('img')].map(i => ({ src: i.src.slice(0, 60), naturalWidth: i.naturalWidth })));
  // stray text after </html>?
  out.trailingText = await page.evaluate(() => document.body.innerText.slice(-80));

  fs.writeFileSync(path.join(EVID, `${name}_od11.json`), JSON.stringify(out, null, 2));
  await browser.close();
  return out;
}

(async () => {
  for (const [name, url] of [
    ['vanilla', 'http://127.0.0.1:8901/radar/vanilla_frontend_od11.html'],
    ['dflash', 'http://127.0.0.1:8901/radar/dflash_frontend_od11.html'],
  ]) {
    const o = await judgeArm(name, url);
    console.log(`=== ${name.toUpperCase()} ===`);
    console.log('console:', JSON.stringify(o.consoleMsgs), 'pageErrors:', JSON.stringify(o.pageErrors));
    console.log('nav:', JSON.stringify(o.components.navLinks.results));
    console.log('search:', JSON.stringify(o.components.search));
    console.log('play:', JSON.stringify(o.components.playButtons.results));
    console.log('create:', JSON.stringify(o.components.createPlaylist));
    console.log('hover:', JSON.stringify(o.components.hover));
    console.log('external:', JSON.stringify(o.externalResources));
    console.log('images:', JSON.stringify(o.imageStatus));
    console.log('trailingText:', JSON.stringify(o.trailingText));
  }
})();
