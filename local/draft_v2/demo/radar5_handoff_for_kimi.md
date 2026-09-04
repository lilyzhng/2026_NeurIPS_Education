# Figure 10 radar update (for Kimi) — replace placeholder values with measured data

The live Figure 10 (5-axis radar, independently scaled axes) carries placeholder
values on two axes. Replace them with the measured numbers from today's runs.
Keep everything else about the figure exactly as is (your visual language:
green solid vanilla markers, pink open DFlash markers, per-axis independent
scales, value pair under each axis label).

## Files

1. `submission/teaching_materials/interactive_site/figures/fig_radar_spec_pilot.svg`
   (the live figure source — this is the one the site embeds)
2. Same-name copies if you keep them in sync: `local/draft_v2/demo/fig_radar_spec_pilot.svg`,
   `local/draft_v2/figures_v4/fig_radar_spec_pilot.png` (2x PNG export)
3. Caption + metric bullet: `submission/teaching_materials/interactive_site/index.html`
   (figcaption near line 635, bullet list near line 625)

## Value changes (only these two axes)

| axis | now (placeholder) | change to | source |
|---|---|---|---|
| Coding | 80 / 80 | **0 / 0** | Terminal-Bench pass rate, 10 tasks, both arms 0 |
| Agentic | 73 / 71 | **61.3 / 82.3** | tau3 retail action match rate (paired_ab: 38/62 vs 51/62) |

Frontend 54.5/45.5, Creative 70/30, Guardrail 80/80 stay unchanged.

Coding axis rendering: both markers at the axis origin (0). Keep the axis and
its label. No asterisk, no footnote, no greying — the caption explains it.
Rescale that axis's ring labels sensibly for a 0 value (or keep the scale and
just plot at center).

## Metric bullet fix (index.html ~line 629)

Change:
    <li>Coding: Terminal-Bench pass rate.</li>
to:
    <li>Coding: Terminal-Bench pass rate (10 tasks).</li>

(Agent bullet already says action match rate — correct, leave it.)

## New caption (replace the figcaption near line 635 verbatim)

<figcaption><strong>Figure 10.</strong> Qwen3-8B with vs without speculative
decoding on LosslessBench. Axes are independently scaled, so each domain's
relative gap is visible. Coding reads 0 / 0: both arms fail all 10
Terminal-Bench tasks — Qwen3-8B sits below this benchmark's task floor, so the
axis detects no quality difference at 8B scale and is scheduled for a retest
with a stronger target model. On the agentic axis the DFlash arm follows the
gold action sequence more closely (82.3% vs 61.3%); at n=10 per domain,
single-task swings are within noise.</figcaption>

## Verify locally, do NOT deploy

Serve `submission/teaching_materials/interactive_site/` (e.g.
`python3 -m http.server 8902` in that dir), open
http://127.0.0.1:8902/#losslessbench, confirm figure + caption, hand the URL
to Lily. She reviews before any vercel deploy.

## Data provenance

- Coding: `local/draft_v2/data/4_6_radar_pilot/coding_results/win_counts.json`
- Agentic action match: `python -m tau2.metrics.paired_ab` over
  `agent_results/{vanilla,dflash}_results.json` (arm_a 38/62 = 61.3%,
  arm_b 51/62 = 82.3%); pass counts 2/10 vs 3/10 are in
  `agent_results/win_counts.json`
