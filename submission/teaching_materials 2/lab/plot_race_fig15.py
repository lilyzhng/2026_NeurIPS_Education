#!/usr/bin/env python3
"""Figure 15: the real decoding race. Horizontal time bars, one lane per config,
all decoding the same 512-token continuation (Figure 1's passage), H100 measured."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

lanes = [  # (label, tok/s median, tau, color)
    ("DSpark",  233.9, "τ 3.5", "#2c5f2d"),
    ("vanilla", 136.2, None,    "#888888"),
    ("EAGLE-3", 128.4, "τ 1.3", "#39598c"),
    ("DFlash (broken)", 115.8, "τ 1.0", "#a84b28"),
]
fig, ax = plt.subplots(figsize=(9, 3.2))
for i, (name, tps, tau, c) in enumerate(lanes):
    secs = 512 / tps
    ax.barh(i, secs, color=c, alpha=0.9, height=0.6)
    note = f"{secs:.2f}s · {tps:.0f} tok/s" + (f" · {tau}" if tau else "")
    ax.text(secs + 0.06, i, note, va="center", fontsize=10)
ax.set_yticks(range(len(lanes)), [l[0] for l in lanes], fontsize=11)
ax.invert_yaxis()
ax.set_xlabel("seconds to decode the same 512-token passage (H100, greedy)")
ax.set_title('The decoding race, run for real: "It does not do to dwell on dreams..."', fontsize=11)
ax.margins(x=0.28)
fig.tight_layout()
out = Path(__file__).resolve().parents[3] / "local/draft_v2/figures_v4/fig15_race_real.png"
fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.3)
print("wrote", out)
