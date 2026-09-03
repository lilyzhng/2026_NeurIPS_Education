#!/usr/bin/env python3
"""Three-axis radar for the spec-only pilot: Qwen3-8B vanilla vs DFlash.

Frontend and creative are GPT-4o rubric means (0-10); guardrail is XSTest
accuracy scaled to 0-10. n=5 per domain, pilot only.
Writes local/draft_v2/figures_v4/fig_radar_spec_pilot.png.
"""
from __future__ import annotations

import json
from math import pi
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "local/draft_v2/data/4_6_radar_pilot"

scores = json.loads((D / "scores.json").read_text())
GUARD_ACC = {"vanilla": 4 / 5, "dflash": 4 / 5}  # scored separately, labels identical

AXES = ["Frontend", "Creative", "Guardrail"]
vals = {}
for arm in ["vanilla", "dflash"]:
    dm = scores[arm]["_domain_means"]
    vals[arm] = [dm["frontend"], dm["creative"], GUARD_ACC[arm] * 10]

angles = [n / 3 * 2 * pi for n in range(3)] + [0]
fig, ax = plt.subplots(figsize=(6.4, 5.6), subplot_kw={"polar": True})
COLORS = {"vanilla": "#4a5a44", "dflash": "#2a6fb0"}
LABELS = {"vanilla": "vanilla Qwen3-8B", "dflash": "+ DFlash draft"}
for arm in ["vanilla", "dflash"]:
    v = vals[arm] + vals[arm][:1]
    ax.plot(angles, v, linewidth=2, color=COLORS[arm], label=LABELS[arm])
    ax.fill(angles, v, alpha=0.12, color=COLORS[arm])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(AXES, fontsize=12)
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=9, color="#888")
ax.legend(loc="lower right", bbox_to_anchor=(1.25, -0.08), fontsize=10, frameon=False)
ax.set_title("Speculative decoding alone: quality pilot (n=5 per domain)",
             fontsize=12, pad=24)
fig.tight_layout(pad=1.6)
out = ROOT / "local/draft_v2/figures_v4/fig_radar_spec_pilot.png"
fig.savefig(out, dpi=180, bbox_inches="tight", pad_inches=0.35)
print("wrote", out, "| values:", vals)
