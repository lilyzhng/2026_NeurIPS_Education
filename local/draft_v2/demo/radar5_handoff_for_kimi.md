# Radar Figure 10 update task (for Kimi) — 3 axes → 5 axes

Update the LosslessBench Figure 10 radar from 3 axes to 5, and replace its
caption. Same visual language as before (you built the current version):
arm A dark green solid markers, arm B pink open markers, domain name with
green value / gray slash / pink value beneath, light polygon grid, legend at
bottom. Grid becomes a pentagon (5 axes).

## Files to touch

1. Figure source: `local/draft_v2/demo/fig_radar_spec_pilot.svg` (edit in place)
2. Export PNG 2x: `local/draft_v2/figures_v4/fig_radar_spec_pilot.png` (overwrite)
3. Copy the SVG to the site:
   `submission/teaching_materials/interactive_site/figures/fig_radar_spec_pilot.svg`
4. Caption: in `submission/teaching_materials/interactive_site/index.html`, find
   the Figure 10 caption under the losslessbench section and replace it with the
   text below.

## New data (5 axes, this order around the pentagon)

| axis label | vanilla Qwen3-8B (green) | + DFlash draft (pink) | metric |
|---|---|---|---|
| Frontend Design | 54.5 | 45.5 | win rate x100, interactive judge, n=11 |
| Creative Writing | 70 | 30 | win rate x100, EQ-Bench judge, n=10 |
| Guardrail | 80 | 80 | accuracy vs gold, n=10 |
| Agent Workflow | 20 | 30 | tau3-bench retail pass rate x100, n=10 |
| Coding | 0 | 0 | Terminal-Bench pass rate x100, n=10 |

Coding axis: draw both markers AT the center (value 0), do NOT omit the axis,
do NOT grey it out, no asterisk, no footnote — the caption carries the
explanation.

## New caption (replace the existing Figure 10 caption verbatim)

Figure 10. Five-domain LosslessBench pilot: vanilla Qwen3-8B (green) vs the
same model with a DFlash draft (pink). Frontend and creative report win rate
x100 (interactive judge, n=11; EQ-Bench judge, n=10); guardrail reports label
accuracy (n=10); agent reports tau3-bench retail pass rate x100 (n=10,
official environment reward); coding reports Terminal-Bench pass rate x100
(n=10). Both arms score 0 on coding: Qwen3-8B sits below Terminal-Bench's
task floor, so this axis detects no quality difference at 8B scale — lossless
verification requires a model inside the benchmark's measurement range, and
this axis is scheduled for a retest with a stronger target model. At n≈10 per
axis, single-task swings are within noise.

## Verify locally, do NOT deploy

Serve `submission/teaching_materials/interactive_site/` locally (e.g.
`python3 -m http.server 8902` in that dir), check #losslessbench renders the
new figure + caption, and hand the preview URL to Lily. No vercel deploy —
Lily reviews first.

## Data provenance (if you want to check the numbers)

- Agent: `local/draft_v2/data/4_6_radar_pilot/agent_results/win_counts.json`
  (vanilla 2/10, dflash 3/10; both-fail-scores-zero rule, JUDGING.md 2026-09-03)
- Coding: `local/draft_v2/data/4_6_radar_pilot/coding_results/win_counts.json`
  (0/10 both arms, half clean fails half 45-min agent timeouts)
