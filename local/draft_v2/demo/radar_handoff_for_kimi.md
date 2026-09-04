# Radar figure task (for Kimi)

Recreate the LosslessBench Figure 10 radar with new data. The ORIGINAL figure source lives in the local site repo:

    ~/Documents/Development/lilyzhng.github.io/writing/losslessbench/radar-v4.svg

(radar-v1 through v4 in the same dir show the iteration history; v4 is the published
version. article.md / index.html in that dir show how it embeds.)

Keep its exact visual language: same fonts, colors handling (arm A dark green solid
markers, arm B pink open markers), label placement (domain name, value pair beneath,
green value / gray slash / pink value), light pentagon grid, per-axis layout, legend at
bottom. The only changes: 3 axes instead of 5, new labels and values below.

## New data

| axis | vanilla Qwen3-8B (green) | + DFlash draft (pink) | metric |
|---|---|---|---|
| Frontend Design | 54.5 | 45.5 | win rate x100, interactive judge, n=11 |
| Creative Writing | 70 | 30 | win rate x100, EQ-Bench judge, n=10 |
| Guardrail | 80 | 80 | accuracy vs gold, n=10 (labels identical across arms) |

Legend labels: "vanilla Qwen3-8B" and "+ DFlash draft".

## Output

Write the new SVG to local/draft_v2/demo/fig_radar_spec_pilot.svg and also export a
PNG at 2x to local/draft_v2/figures_v4/fig_radar_spec_pilot.png (overwrite).

Reference only (do not imitate): a matplotlib attempt lives at
submission/teaching_materials/lab/plot_radar_pilot.py — the data-loading part at the
top shows where the win counts come from if you want to recompute them.
