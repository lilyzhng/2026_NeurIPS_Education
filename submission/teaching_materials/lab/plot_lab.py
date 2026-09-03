#!/usr/bin/env python3
"""Plots for the lab data. Quick working versions; final article figures get
restyled via the paper figure pipeline.

  python3 plot_lab.py race    # 4_2_race.json  -> fig6_lab_race.png (lanes by algo x domain)
  python3 plot_lab.py sweep   # 4_3_sweep.json -> fig12_threshold_sweep_real.png

Reads from local/draft_v2/data/, writes to local/draft_v2/figures_v4/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3] / "local/draft_v2"
DATA, FIGS = ROOT / "data", ROOT / "figures_v4"


def median_toks(runs: list[dict]) -> float:
    vals = sorted(r["tokens_per_s"] for r in runs if r.get("tokens_per_s"))
    return vals[len(vals) // 2]


def plot_race() -> None:
    data = json.loads((DATA / "4_2_race.json").read_text())
    labels, domains = list(data), ["coding", "creative", "frontend"]
    fig, ax = plt.subplots(figsize=(9, 0.6 * len(labels) * len(domains) + 1.5))
    colors = {"coding": "#2c5f2d", "creative": "#97662a", "frontend": "#39598c"}
    y, ticks, names = 0, [], []
    for label in labels:
        for d in domains:
            if d not in data[label]:
                continue
            toks = median_toks(data[label][d]["runs"])
            ax.barh(y, toks, color=colors[d], alpha=0.85)
            ax.text(toks + 2, y, f"{toks:.0f} tok/s", va="center", fontsize=9)
            ticks.append(y)
            names.append(f"{label} · {d}")
            y += 1
        y += 0.6
    ax.set_yticks(ticks, names, fontsize=9)
    ax.set_xlabel("median decode tokens/s (512-token generations, H100)")
    ax.set_title("The decoding race, measured: algorithms x domains")
    ax.margins(x=0.15)  # generous right padding
    fig.tight_layout()
    out = FIGS / "fig6_lab_race.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.3)
    print("wrote", out)


def plot_sweep() -> None:
    data = json.loads((DATA / "4_3_sweep.json").read_text())
    # expected shape: {"0.9": {"tokens_per_s":..., "accept_length":..., "accuracy":...}, ...}
    ths = sorted(data, key=float, reverse=True)
    speed = [data[t].get("tokens_per_s") for t in ths]
    acc = [data[t].get("accuracy") for t in ths]
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(ths, speed, "o-", color="#39598c", label="tokens/s")
    ax1.set_xlabel("confidence threshold (strict -> loose)")
    ax1.set_ylabel("tokens/s", color="#39598c")
    ax2 = ax1.twinx()
    ax2.plot(ths, acc, "s--", color="#a84b28", label="task accuracy")
    ax2.set_ylabel("task accuracy", color="#a84b28")
    ax1.set_title("Relaxing acceptance: speed up, accuracy down")
    ax1.margins(x=0.12)
    fig.tight_layout()
    out = FIGS / "fig12_threshold_sweep_real.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.3)
    print("wrote", out)


if __name__ == "__main__":
    {"race": plot_race, "sweep": plot_sweep}[sys.argv[1]]()
