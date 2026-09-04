#!/usr/bin/env python3
"""Figure: per-domain acceptance length (tau) and divergence (D_LK) for DFlash.

Reads data/4_7_alpha_divergence/measured_alpha.json, writes
figures_v4/fig_alpha_divergence.png. Two panels, one shared domain axis:
gray = benchmarks from the DFlash paper, teal = LosslessBench domains.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
data = json.loads((ROOT / "local/draft_v2/data/4_7_alpha_divergence/measured_alpha.json").read_text())

ORDER = ["gsm8k_paper", "humaneval_paper", "frontend_design", "coding",
         "agentic_workflow", "safety_guardrail", "creative_writing"]
LABELS = ["GSM8K\n(paper)", "HumanEval\n(paper)", "Frontend\ndesign", "Agentic\ncoding",
          "Agentic\nworkflow", "Safety\nguardrail", "Creative\nwriting"]
PAPER = "#9aa3ab"
BENCH = "#2a7f8f"
colors = [PAPER, PAPER, BENCH, BENCH, BENCH, BENCH, BENCH]

taus = [data[d]["tau"] for d in ORDER]
dlks = [data[d]["divergence_dlk"] for d in ORDER]
per_tau = [[p["tau"] for p in data[d]["prompts"] if p["tau"]] for d in ORDER]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 3.8), dpi=200)

x = range(len(ORDER))
ax1.bar(x, taus, color=colors, width=0.62, zorder=2)
for i, (v, pts) in enumerate(zip(taus, per_tau)):
    lo, hi = min(pts), max(pts)
    ax1.vlines(i, lo, hi, color="#30343a", lw=1.2, zorder=3)
    for y in (lo, hi):
        ax1.hlines(y, i - 0.09, i + 0.09, color="#30343a", lw=1.2, zorder=3)
    ax1.text(i, hi + 0.22, f"{v:.2f}", ha="center", fontsize=8.5, color="#30343a")
ax1.set_ylabel("Acceptance length τ (tokens/cycle)")
ax1.set_title("Acceptance length by domain", fontsize=10)
ax1.set_ylim(0, max(max(p) for p in per_tau) + 1.0)

ax2.bar(x, dlks, color=colors, width=0.62, zorder=2)
for i, v in enumerate(dlks):
    ax2.text(i, v + 0.015, f"{v:.2f}", ha="center", fontsize=8.5, color="#30343a")
ax2.set_ylabel("Divergence  $D_{LK}$ = 1 − α")
ax2.set_title("Draft–target distributional divergence", fontsize=10)
ax2.set_ylim(0, 1.05)

for ax in (ax1, ax2):
    ax.set_xticks(list(x))
    ax.set_xticklabels(LABELS, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e3e6e9", lw=0.8, zorder=0)
    ax.tick_params(length=0)

handles = [plt.Rectangle((0, 0), 1, 1, color=PAPER), plt.Rectangle((0, 0), 1, 1, color=BENCH)]
fig.legend(handles, ["DFlash paper benchmarks", "LosslessBench domains"],
           loc="upper center", ncol=2, frameon=False, fontsize=8.5,
           bbox_to_anchor=(0.5, 1.04))
fig.suptitle("")
fig.text(0.01, -0.06,
         "DFlash (z-lab/Qwen3-8B-DFlash-b16) on Qwen3-8B, vLLM strict verification, temperature=1, "
         "thinking off, 5 original tasks per axis (agentic coding = Terminal-Bench 2, agentic workflow = tau2-bench); whiskers = min–max over tasks. α = 1 − $D_{LK}$ (Leviathan et al. 2023, Thm 3.5).",
         fontsize=7, color="#6a7076")
fig.tight_layout()
out = ROOT / "local/draft_v2/figures_v4/fig_alpha_divergence.png"
fig.savefig(out, bbox_inches="tight", pad_inches=0.35)
print("saved ->", out)
