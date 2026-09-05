# Interactive Frontend Judge Protocol (v1, 2026-09-03)

Executor: Kimi (kimi-code CLI). Designer: Claude/Lily. Derived from OpenDesign's
interactive judging protocol (`code_aesthetics/OpenDesign/scripts/util/arena_judge_prompt.py`,
`SYSTEM_PROMPT_HTML_AESTHETIC`), adapted from screenshot-agent form to
Playwright-driven form.

## Why this exists

A static-screenshot judge (GPT-4o on one image) scored a page 87/100 whose
calendar cannot select any date and whose grid overflows the popup. Webpages
are interactions. The judge must interact.

## Inputs

16 single-file HTML pages, two arms x 8 briefs, all generated greedily by the
same model (Qwen3-8B), so any difference between arms is trajectory divergence:

- Pages: `local/draft_v2/demo/{vanilla,dflash}_raw.html` (brief od673) and
  `local/draft_v2/demo/radar/{vanilla,dflash}_frontend_{od5,od6,od8,od9,od10,od340,od341}.html`
- Briefs: the `BRIEFS` dict in `submission/teaching_materials/lab/build_compare_page.py`
- Serve the `local/draft_v2/demo/` directory locally (any port) before testing;
  test over http, not file://, so fetch/JS behave normally.

## Procedure per page (both dimensions, in order)

### Dimension 1: code correctness (0-40)

Read the source. Score down for, with one line of evidence each:
- Truncated or malformed HTML (unclosed tags, stray markdown fences)
- Violation of the brief's constraints (all briefs required a complete
  single-file page, inline CSS, no external assets; an external image URL is
  a violation even if it looks better)
- JS errors on load (check the browser console via Playwright)
- Dead code: handlers defined but never attached, CSS selectors matching nothing

### Dimension 2: component functionality (0-60)

OpenDesign's rules, executed with Playwright:

1. **Plan first.** From the brief and the rendered page, list every component a
   user would expect to interact with (buttons, day cells, inputs, hovers,
   close icons, nav links). Write the plan down before acting.
2. **Interact in plan order.** For each component, capture state before, act,
   capture state after. State = DOM snapshot plus a screenshot when visual.
3. **The page must change according to the interaction.** No change, or a
   wrong change, scores zero for that component. Correct-and-logical feedback
   only. (OpenDesign: "Only correct feedback can earn points.")
4. **Text inputs**: typing alone is not success. Type, then submit/click the
   associated button; the page must respond to the submission.
5. **Hover requirements in the brief** (od340's 3D flip) are tested with
   Playwright hover; the computed transform must actually change.
6. **Already-there navigation**: if clicking nav appears inert because the page
   is already at the target, click another nav item and come back.
7. Offline pages: do not penalize for missing network-dependent behavior.

Functionality score = 60 x (components with correct feedback / components
planned), weighted double for components the brief explicitly asks for
(the calendar's date selection, od340's flip, od341's subscribe flow).

## Output contract

Write exactly one file:
`local/draft_v2/data/4_6_radar_pilot/scores_interactive.json`

```json
{
  "vanilla": {
    "od673": {
      "code_correctness": 0-40,
      "functionality": 0-60,
      "total": 0-100,
      "planned_components": ["..."],
      "dead_components": [{"component": "...", "evidence": "clicked day cell 2, no class or DOM change"}],
      "code_issues": ["..."],
      "feedback": "<= 40 words"
    },
    "...": {}
  },
  "dflash": {}
}
```

Also write a short human-readable summary to
`local/draft_v2/data/4_6_radar_pilot/interactive_report.md`: per-arm means,
the three worst pages with their evidence, and any case where this score
disagrees with the static GPT-4o score (`scores_opendesign.json`) by more
than 20 points.

## Ground rules

- Judge both arms with identical procedure and thresholds. Never fix or edit
  the generated pages.
- Every deduction needs recorded evidence (what you did, what happened).
- Determinism: pages are static artifacts; run interactions twice if a result
  seems flaky and keep the reproducible outcome.
- Do not touch anything outside the two output files and your own scratch
  directory (`submission/teaching_materials/lab/kimi_judge_scratch/`).
