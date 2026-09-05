#!/usr/bin/env python3
"""Win-count radar, styled after the original Figure 10 (fig9_radar_five_domains).

Each axis = win count / n (tie scores one point for each side).
Frontend: interactive judge. Creative: EQ-Bench CW v3 judge. Guardrail: labels vs gold.
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

inter = json.loads((D / "scores_interactive.json").read_text())
eq = json.loads((D / "scores_eqbench_cw3.json").read_text())


def win_counts(pairs):
    w = {"vanilla": 0, "dflash": 0}
    n = 0
    for a, b in pairs:
        if a is None or b is None:
            continue
        n += 1
        if a > b: w["vanilla"] += 1
        elif b > a: w["dflash"] += 1
        else: w["vanilla"] += 1; w["dflash"] += 1
    return w, n


front_ids = sorted(set(inter["vanilla"]) & set(inter["dflash"]))
fw, n_f = win_counts([(inter["vanilla"][i]["total"], inter["dflash"][i]["total"])
                      for i in front_ids])
cr_ids = [k for k in eq["vanilla"] if not k.startswith("_")]
cw, n_c = win_counts([(eq["vanilla"][i]["eqbench_score_0_20"],
                       eq["dflash"][i]["eqbench_score_0_20"]) for i in cr_ids])
gw, n_g = {"vanilla": 8, "dflash": 8}, 10  # accuracy vs gold, labels identical across arms

DOMAINS = [
    ("Frontend Design", fw, n_f),
    ("Creative Writing", cw, n_c),
    ("Guardrail", gw, n_g),
]

GREEN, PINK = "#2d5e3f", "#d4548a"
BG = "#faf8f4"

vals = {arm: [w[arm] / n for _, w, n in DOMAINS] for arm in ["vanilla", "dflash"]}
N = len(DOMAINS)
angles = [pi / 2 + i * 2 * pi / N for i in range(N)]

fig, ax = plt.subplots(figsize=(8.2, 7.6), subplot_kw={"polar": True})
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for arm, color, mfc in [("vanilla", GREEN, GREEN), ("dflash", PINK, "white")]:
    v = vals[arm] + vals[arm][:1]
    a = angles + angles[:1]
    ax.plot(a, v, color=color, linewidth=2.5, zorder=3,
            marker="o", markersize=9, markerfacecolor=mfc,
            markeredgecolor=color, markeredgewidth=2.2)
    ax.fill(a, v, color=color, alpha=0.08, zorder=2)

ax.set_xticks(angles)
ax.set_xticklabels([])
ax.set_ylim(0, 1.02)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels([])
ax.grid(color="#e4e0d6", linewidth=1)
ax.spines["polar"].set_color("#e4e0d6")

# Labels in screen coordinates: name pushed outward from each vertex,
# score pair centered directly under the name.
fig.canvas.draw()
inv = fig.transFigure.inverted()
import numpy as np
cx, cy = inv.transform(ax.transData.transform((0, 0)))
for ang, (name, w, n) in zip(angles, DOMAINS):
    vx, vy = inv.transform(ax.transData.transform((ang, 1.0)))
    dx, dy = vx - cx, vy - cy
    norm = (dx ** 2 + dy ** 2) ** 0.5
    ux, uy = dx / norm, dy / norm
    nx, ny = vx + ux * 0.055, vy + uy * 0.055
    def fmt(x):
        v = x * 100
        return f"{v:.1f}".rstrip("0").rstrip(".")
    fig.text(nx, ny, name, ha="center", va="center",
             fontsize=15, fontweight="bold", color="#1f1f1c")
    sy = ny - 0.034
    fig.text(nx - 0.008, sy, fmt(w["vanilla"] / n), ha="right", va="center",
             fontsize=13, fontweight="bold", color=GREEN)
    fig.text(nx, sy, "/", ha="center", va="center", fontsize=13, color="#999")
    fig.text(nx + 0.008, sy, fmt(w["dflash"] / n), ha="left", va="center",
             fontsize=13, fontweight="bold", color=PINK)

from matplotlib.lines import Line2D
handles = [
    Line2D([], [], color=GREEN, marker="o", markersize=9, markerfacecolor=GREEN,
           linewidth=2.5, label="vanilla Qwen3-8B"),
    Line2D([], [], color=PINK, marker="o", markersize=9, markerfacecolor="white",
           markeredgecolor=PINK, markeredgewidth=2.2, linewidth=2.5,
           label="+ DFlash draft"),
]
fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
           fontsize=13, bbox_to_anchor=(0.5, 0.015))
fig.subplots_adjust(top=0.82, bottom=0.14, left=0.12, right=0.88)

out = ROOT / "local/draft_v2/figures_v4/fig_radar_spec_pilot.png"
fig.savefig(out, dpi=180, facecolor=BG, bbox_inches="tight", pad_inches=0.45)
print("wrote", out, "| wins:", {k: v for k, (_, v, n) in zip(["f","c","g"], DOMAINS)})
