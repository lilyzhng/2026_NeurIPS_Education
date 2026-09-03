const { chromium } = require('playwright');
const fs = require('fs');

const ARMS = {
  vanilla: 'http://127.0.0.1:8901/vanilla_raw.html',
  dflash: 'http://127.0.0.1:8901/dflash_raw.html',
};

async function judgeArm(name, url) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });
  const consoleMsgs = [];
  page.on('console', m => { if (m.type() === 'error') consoleMsgs.push(m.text()); });
  page.on('pageerror', e => consoleMsgs.push('PAGEERROR: ' + e.message));

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(500);

  const out = { consoleErrors: consoleMsgs, steps: {} };

  // --- Step 0: initial DOM snapshot ---
  out.steps.initial = await page.evaluate(() => {
    const modal = document.getElementById('calendarModal');
    const btn = document.querySelector('.calendar-button') || document.getElementById('openCalendar');
    const days = document.querySelectorAll('.calendar-day, .calendar td');
    const grid = document.getElementById('calendarGrid') || document.getElementById('calendarBody');
    const gridRows = grid ? grid.querySelectorAll('tr').length : -1;
    return {
      buttonText: btn ? btn.textContent.trim() : null,
      modalDisplay: modal ? getComputedStyle(modal).display : null,
      modalVisible: modal ? getComputedStyle(modal).visibility : null,
      dayCellCount: days.length,
      numberedDays: [...days].filter(d => /\d+/.test(d.textContent)).map(d => d.textContent.trim()).slice(0, 40),
      header: (document.getElementById('calendarHeader') || {}).textContent || null,
      gridRows,
      gridChildTags: grid ? [...grid.children].slice(0, 5).map(c => c.tagName) : [],
      bodyScrollW: document.body.scrollWidth,
    };
  });
  await page.screenshot({ path: `evidence/od673_${name}_0_initial.png` });

  // --- Step 1: click "Open Calendar" button ---
  const btnSel = name === 'vanilla' ? '.calendar-button' : '#openCalendar';
  await page.click(btnSel);
  await page.waitForTimeout(600);
  out.steps.afterOpen = await page.evaluate(() => {
    const modal = document.getElementById('calendarModal');
    const cs = getComputedStyle(modal);
    const r = modal.getBoundingClientRect();
    const backdrop = document.getElementById('backdrop');
    return {
      modalDisplay: cs.display,
      modalOpacity: cs.opacity,
      modalVisibility: cs.visibility,
      modalRect: { w: Math.round(r.width), h: Math.round(r.height), x: Math.round(r.x), y: Math.round(r.y) },
      backdropOpacity: backdrop ? getComputedStyle(backdrop).opacity : null,
      classes: modal.className,
    };
  });
  await page.screenshot({ path: `evidence/od673_${name}_1_open.png` });

  // --- Step 2: date selection (brief-explicit, x2) ---
  // pick a numbered day cell that is not "today"
  const dayInfo = await page.evaluate(() => {
    const cells = [...document.querySelectorAll('.calendar-day, .calendar td')].filter(c => /^\d+$/.test(c.textContent.trim()));
    const target = cells.find(c => !c.classList.contains('today') && c.textContent.trim() !== '') || cells[0];
    return { count: cells.length, targetText: target ? target.textContent.trim() : null };
  });
  out.steps.dayCells = dayInfo;
  const cellSel = name === 'vanilla' ? '.calendar-day' : '.calendar td';
  const cells = await page.$$(cellSel);
  let clicked = null;
  for (const c of cells) {
    const t = (await c.textContent()).trim();
    const cls = await c.getAttribute('class');
    if (/^\d+$/.test(t) && !(cls || '').includes('today')) { clicked = c; break; }
  }
  const before = clicked ? await clicked.evaluate(el => ({ cls: el.className, bg: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color })) : null;
  if (clicked) await clicked.click();
  await page.waitForTimeout(400);
  const after = clicked ? await clicked.evaluate(el => ({ cls: el.className, bg: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color })) : null;
  const anySelected = await page.evaluate(() => document.querySelectorAll('.selected').length);
  out.steps.dateSelection = { before, after, anySelectedCount: anySelected };
  await page.screenshot({ path: `evidence/od673_${name}_2_select.png` });

  // --- Step 3: hover feedback on a day cell ---
  if (clicked) {
    const hBefore = await clicked.evaluate(el => getComputedStyle(el).backgroundColor);
    await clicked.hover();
    await page.waitForTimeout(300);
    const hAfter = await clicked.evaluate(el => getComputedStyle(el).backgroundColor);
    out.steps.hover = { before: hBefore, after: hAfter, changed: hBefore !== hAfter };
  }

  // --- Step 4: close the modal ---
  if (name === 'vanilla') {
    await page.click('.close-btn');
  } else {
    // dflash: close via backdrop click (only close affordance present)
    const closeBtn = await page.$('.close-btn');
    out.steps.closeBtnExists = !!closeBtn;
    await page.mouse.click(20, 20); // backdrop area top-left
  }
  await page.waitForTimeout(600);
  out.steps.afterClose = await page.evaluate(() => {
    const modal = document.getElementById('calendarModal');
    const cs = getComputedStyle(modal);
    return { display: cs.display, opacity: cs.opacity, visibility: cs.visibility, classes: modal.className };
  });
  await page.screenshot({ path: `evidence/od673_${name}_3_closed.png` });

  // --- Step 5: reopen to confirm toggle works both ways ---
  await page.click(btnSel);
  await page.waitForTimeout(500);
  out.steps.reopen = await page.evaluate(() => {
    const modal = document.getElementById('calendarModal');
    return { display: getComputedStyle(modal).display, classes: modal.className };
  });

  await browser.close();
  return out;
}

(async () => {
  const res = {};
  for (const [name, url] of Object.entries(ARMS)) {
    res[name] = await judgeArm(name, url);
  }
  fs.writeFileSync('evidence/od673_interactions.json', JSON.stringify(res, null, 2));
  console.log(JSON.stringify(res, null, 2));
})();
