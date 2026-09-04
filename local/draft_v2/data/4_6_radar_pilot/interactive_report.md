## Win-count summary (LosslessBench convention: 1 point per task won, null 50/50)

| judge | vanilla wins | DFlash wins | ties | sign-test read |
|---|---|---|---|---|
| interactive (Kimi, this protocol) | 5 | 3 | 0 | p ≈ 0.73, no difference |
| static (GPT-4o screenshot) | 1 | 2 | 5 | no difference |

Per-task interactive results (vanilla vs DFlash): od10 83:67, od340 27:87, od341 85:76, od5 40:100, od6 68:61, od673 95:68, od8 96:78, od9 55:64

Note the aggregation sensitivity: mean-of-scores favors DFlash (+6.5) while
win count favors vanilla (5:3). Two aggregations, two directions, one dataset:
the arms are not distinguishable at n=8. Two 60-point single-trajectory swings
(od5, od340) drive the mean; the win count absorbs them as one win each.

---

# Interactive judge report (Playwright-driven, 2026-09-03)

Protocol: `submission/teaching_materials/lab/interactive_judge_protocol.md`. Each page scored on code correctness (0-40, source + console audit) and component functionality (0-60, every planned component clicked/hovered/submitted in headless Chromium; brief-explicit components weighted x2). Raw evidence in `submission/teaching_materials/lab/kimi_judge_scratch/`.

## Per-arm means

- **vanilla: 68.6** (code 36.0/40, functionality 32.6/60)
- **dflash: 75.1** (code 33.9/40, functionality 41.2/60)

dflash stays ahead under interactive judging (static GPT-4o means: vanilla 75.1, dflash 81.0), but the margin narrows once dead components are priced in. The functionality dimension is what separates the arms (vanilla 32.6 vs dflash 41.2): vanilla ships more pages that look finished but have no working interactivity (od5, od9, od340).

## All scores (interactive vs static GPT-4o)

| brief | vanilla inter | vanilla static | delta | dflash inter | dflash static | delta |
|---|---|---|---|---|---|---|
| od673 Translucent calendar popup | 95 | 87 | +8 | 68 | 87 | -19 |
| od5 Life insurance UI | 40 | 87 | -47 | 100 | 87 | +13 |
| od6 Dog products landing | 68 | 87 | -19 | 61 | 87 | -26 |
| od8 Airbnb group adventures | 96 | 66 | +30 | 78 | 87 | -9 |
| od9 Vehicle loans iOS app | 55 | 87 | -32 | 64 | 87 | -23 |
| od10 Ghibli animation studio | 83 | 70 | +13 | 67 | 63 | +4 |
| od340 Photo card 3D hover flip | 27 | 30 | -3 | 87 | 63 | +24 |
| od341 Newsletter popup | 85 | 87 | -2 | 76 | 87 | -11 |

## Three worst pages, with evidence

### vanilla od340 (Photo card 3D hover flip) — 27/100 (code 27, functionality 0)
- DEAD: **card hover 3D flip (brief, x2)** — page.hover('.card') does change computed transform (none -> matrix3d(-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1)), but neither .face is pre-rotated rotateY(180deg), so after the 180deg flip both faces are backface-hidden and the card vanishes completely (screenshot vanilla_hover.png: empty page). Wrong feedback: flip reveals a blank card, not a back face. Also the back .face is stacked on top initially, so the card shows the 'Back' broken-image alt text instead of the front photo.
- code: External asset violation: two <img src="https://via.placeholder.com/300x200"> (offline-hostile external URLs) (-8, incl. host being dead)
- code: via.placeholder.com fails even with network: console error 'Failed to load resource: net::ERR_CONNECTION_CLOSED', requestfailed ERR_CONNECTION_CLOSED, img naturalWidth=0 -> no photo ever renders (-2)
- code: Stray markdown fence '```' after </html> renders as visible text on the page (-3)
- code: Structural CSS bug: back face missing transform: rotateY(180deg) (primary penalty taken in functionality)

### vanilla od5 (Life insurance UI) — 40/100 (code 40, functionality 0)
- DEAD: **nav links** — clicked nav 'About' (href="#"): URL only changed ...od5.html -> ...od5.html#, scrollY stayed 0, no DOM/content change
- DEAD: **hero 'Get a Quote' CTA button** — button has no event handler in source; clicked it, URL and scrollY unchanged, zero page feedback
- DEAD: **CTA form submit** — filled name='Jane Doe', email, clicked 'Get Started': browser-default GET reload appended '?' to URL and cleared fields; no confirmation message or designed feedback
- DEAD: **footer social links** — clicked 'Facebook' (href="#"): URL ...od5.html -> ...od5.html#, no navigation or feedback

### vanilla od9 (Vehicle loans iOS app) — 55/100 (code 40, functionality 15)
- DEAD: **hero 'Get Started' button** — clicked; no onclick attribute, no dialog, no DOM/hash/scroll change (bodyHTMLlen unchanged at 1300)
- DEAD: **footer 'Privacy Policy' link** — href='#' placeholder; clicked from scrollY=248, only scrolled to top, no content/navigation
- DEAD: **footer 'Terms of Service' link** — href='#' placeholder; clicked from scrollY=248, only scrolled to top, no content/navigation

## Disagreements with the static GPT-4o score (>20 pts)

- **vanilla od5**: interactive 40 vs static 87 (-47). Failed/dead components: nav links; hero 'Get a Quote' CTA button; CTA form submit; footer social links.
- **vanilla od8**: interactive 96 vs static 66 (+30). Failed/dead components: none dead.
- **vanilla od9**: interactive 55 vs static 87 (-32). Failed/dead components: hero 'Get Started' button; footer 'Privacy Policy' link; footer 'Terms of Service' link.
- **dflash od6**: interactive 61 vs static 87 (-26). Failed/dead components: nav About link; Add to Cart buttons; Subscribe Now button; footer links.
- **dflash od9**: interactive 64 vs static 87 (-23). Failed/dead components: footer 'Privacy Policy' link; footer 'Terms of Service' link; footer 'Contact Us' link.
- **dflash od340**: interactive 87 vs static 63 (+24). Failed/dead components: none dead.

---

# Addendum: od11 / od20 / od28 (judged 2026-09-03, same protocol)

Briefs: od11 Spotify-like music UI (navigation + playlist creation), od20 traffic-data dashboard with interactive charts, od28 interactive charts for trading trends + NY accident statistics. Same procedure, same thresholds, raw evidence in `submission/teaching_materials/lab/kimi_judge_scratch/{scripts,evidence}/`.

## Scores (interactive vs static GPT-4o)

| brief | vanilla inter | vanilla static | delta | dflash inter | dflash static | delta |
|---|---|---|---|---|---|---|
| od11 Spotify clone | 48 | 87 | -39 | 37 | 87 | -50 |
| od20 Traffic dashboard | 20 | 63 | -43 | 37 | 82 | -45 |
| od28 Trading + accidents | 5 | 20 | -15 | 17 | 35 | -18 |

Win count on the new pages: vanilla 1 (od11), dflash 2 (od20, od28).

## Key findings

- **Both od11 pages are dead shells.** Nav links are `href="#"` placeholders, search input does nothing on Enter, all three Play buttons have no handlers, and the brief's core ask — playlist creation — is fully dead in both arms (typed name + click: card count 3->3, zero DOM/text change). Only CSS hover works. vanilla is cleaner code (data-URI images, 38/40); dflash violates single-file with three `via.placeholder.com` images that fail even online (`ERR_CONNECTION_CLOSED`, naturalWidth=0) plus a rendered stray fence (27/40).
- **vanilla od20 is truncated mid-statement.** Source ends at `const barWidth = chartWidth / (data.length -`; the unterminated script block never executes, so both canvases render blank (0 painted pixels) and the tooltip handlers that would have satisfied "interactive" never attach. dflash od20 actually draws both charts (5.8k / 27k painted pixels) but ships **zero event listeners** — no tooltips, no click response — so it also scores 0 on functionality against a brief that explicitly demands interactive charts.
- **od28 failed to generate in both arms, differently.** vanilla is a 79-byte file cut off inside the `<title>` tag — blank page. dflash saved its chain-of-thought as the deliverable: title + two empty chart boxes, then ~9.9k chars of visible reasoning prose, including a live `<script>` that throws `ReferenceError: d3 is not defined` on load (D3 would have violated the no-external-assets rule regardless; the leaked prose even shows the model realizing this mid-stream).

## Disagreements with static GPT-4o (>20 pts)

All four chartable disagreements run the same direction — static over-scored dead pages:
- **vanilla od11**: 48 vs 87 (-39). Dead: nav, search, Play buttons, create-playlist flow.
- **dflash od11**: 37 vs 87 (-50). Same dead set, plus broken external images.
- **vanilla od20**: 20 vs 63 (-43). Blank canvases; GPT-4o saw "placeholders for charts" but the interactive score prices in that nothing can ever run.
- **dflash od20**: 37 vs 82 (-45). GPT-4o credited "interactive charts"; the page has zero event listeners.
