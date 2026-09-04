# Figure 10 radar update (for Kimi) — coding axis only

One change: the coding axis of the Figure 10 radar carries a placeholder
(80 / 80). Replace it with the measured result: **0 / 0**. Touch nothing else
on the figure — all other axes (Frontend 54.5/45.5, Creative 70/30,
Guardrail 80/80, Agentic 73/71) stay exactly as they are; the agentic axis is
mid-evaluation and will be updated in a later pass. Keep your visual language
unchanged (green solid vanilla markers, pink open DFlash markers, per-axis
independent scales, value pair under each axis label).

## Files

1. `submission/teaching_materials/interactive_site/figures/fig_radar_spec_pilot.svg`
   (the live figure source — this is the one the site embeds)
2. Keep the sibling copies in sync: `local/draft_v2/demo/fig_radar_spec_pilot.svg`,
   `local/draft_v2/figures_v4/fig_radar_spec_pilot.png` (2x PNG export)
3. Caption: `submission/teaching_materials/interactive_site/index.html`
   (figcaption near line 635)

## The change

| axis | now (placeholder) | change to | source |
|---|---|---|---|
| Coding | 80 / 80 | **0 / 0** | Terminal-Bench pass rate, 10 tasks, both arms 0 |

Rendering: both markers at the axis origin (0). Keep the axis and its label.
No asterisk, no footnote, no greying — the caption explains it. Rescale that
axis's ring labels sensibly for a 0 value (or keep the scale and just plot at
center).

## New caption (replace the figcaption near line 635 verbatim)

<figcaption><strong>Figure 10.</strong> Qwen3-8B with vs without speculative
decoding on LosslessBench. Axes are independently scaled, so each domain's
relative gap is visible. Coding reads 0 / 0: both arms fail all 10
Terminal-Bench tasks — Qwen3-8B sits below this benchmark's task floor, so the
axis detects no quality difference at 8B scale and is scheduled for a retest
with a stronger target model.</figcaption>

## Verify locally, do NOT deploy

Serve `submission/teaching_materials/interactive_site/` (e.g.
`python3 -m http.server 8902` in that dir), open
http://127.0.0.1:8902/#losslessbench, confirm figure + caption, hand the URL
to Lily. She reviews before any vercel deploy.

## Data provenance

`local/draft_v2/data/4_6_radar_pilot/coding_results/win_counts.json`
(10 pinned Terminal-Bench tasks, harbor terminus-2, both arms 0 passes:
mix of clean failures and 45-minute agent timeouts).
