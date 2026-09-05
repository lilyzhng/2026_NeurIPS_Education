#!/usr/bin/env python3
"""Build compare_coding.html: side-by-side Terminal-Bench trial viewer.

Reads jobs/radar_tb2_{vanilla,dflash}/<task>__*/agent/trajectory.json from the
LosslessBench repo and renders each pinned task as left/right step timelines
with the verifier outcome (all 0 in the pilot: the page shows HOW each arm
fails, which is the teaching point).

  python3 build_compare_coding.py
"""
from __future__ import annotations

import glob
import html
import json
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
JOBS = Path.home() / "Documents/lily-memory/Build/LosslessBench/jobs"
SITE = ROOT / "submission/teaching_materials/interactive_site"
TASKS = json.loads(
    (ROOT / "local/draft_v2/data/4_6_radar_pilot/coding_results/win_counts.json").read_text()
)["task_ids"]


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def load_trial(arm: str, task: str):
    hits = glob.glob(str(JOBS / f"radar_tb2_{arm}" / f"{task}__*"))
    if not hits:
        return None
    d = Path(hits[0])
    out = {"exception": None, "steps": []}
    rj = d / "result.json"
    if rj.is_file():
        r = json.loads(rj.read_text())
        exc = r.get("exception_info") or {}
        if exc.get("exception_type"):
            out["exception"] = f"{exc.get('exception_type')}: {str(exc.get('exception_message'))[:120]}"
    tj = d / "agent" / "trajectory.json"
    if tj.is_file():
        t = json.loads(tj.read_text())
        steps = t if isinstance(t, list) else t.get("steps") or []
        for s in steps:
            if isinstance(s, dict) and s.get("message"):
                out["steps"].append(str(s["message"]))
    return out


def render_cell(arm_label: str, trial) -> str:
    if not trial:
        return f'<div class="cell"><div class="head"><b>{arm_label}</b></div><div class="trace">no trial data</div></div>'
    n = len(trial["steps"])
    verdict = trial["exception"] or f"agent finished on its own after {n} steps"
    rows = []
    for i, msg in enumerate(trial["steps"]):
        first = msg.split("\n")[0][:150]
        rows.append(
            f'<details><summary><span class="n">{i+1}</span> {esc(first)}</summary>'
            f"<div>{esc(msg[:4000])}</div></details>"
        )
    cls = "to" if trial["exception"] else ""
    return (
        f'<div class="cell"><div class="head"><b>{arm_label}</b>'
        f'<span class="sc">reward 0 &middot; {n} steps</span></div>'
        f'<div class="verdict {cls}">{esc(verdict)}</div>'
        f'<div class="trace">{"".join(rows)}</div></div>'
    )


def main() -> None:
    blocks = []
    for task in TASKS:
        van, dfl = load_trial("vanilla", task), load_trial("dflash", task)
        blocks.append(
            f'<div class="brief"><b>{esc(task)}</b> &middot; both models score 0 (verifier tests fail)</div>'
            f'<div class="pair">{render_cell("vanilla Qwen3-8B", van)}{render_cell("+ DFlash draft", dfl)}</div>'
        )
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Coding: Terminal-Bench trials, both models</title>
<style>
  body {{ margin:0; padding:24px; font-family:'ET Book', Palatino, Georgia, serif; background:#fffffb; color:#111; }}
  h1 {{ font-size:22px; }} .sub {{ color:#555; font-size:14.5px; max-width:900px; }}
  .brief {{ margin:26px 0 8px; font-size:15px; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .cell {{ border:1px solid #e2e2da; border-radius:12px; overflow:hidden; background:#fff; }}
  .head {{ display:flex; gap:10px; align-items:baseline; padding:8px 13px; background:#1e2a1c; color:#fff; font-size:14px; }}
  .sc {{ font-size:12px; color:#b9c7b2; }}
  .verdict {{ padding:6px 13px; font-size:12.5px; color:#2c5f2d; border-bottom:1px solid #eee; }}
  .verdict.to {{ color:#a33; }}
  .trace {{ height:340px; overflow-y:auto; padding:8px 12px; font-size:12px; }}
  details {{ margin:3px 0; }}
  summary {{ cursor:pointer; color:#333; }}
  summary .n {{ display:inline-block; min-width:20px; color:#999; font-family:-apple-system,sans-serif; font-size:10px; }}
  details > div {{ white-space:pre-wrap; background:#f6f6f0; border-radius:8px; padding:8px 10px; margin:4px 0 6px 22px;
                   font-family:ui-monospace,Menlo,monospace; font-size:11px; max-height:260px; overflow-y:auto; }}
</style></head><body>
<h1>Coding: Terminal-Bench, vanilla Qwen3-8B (left) vs + DFlash draft (right)</h1>
<div class="sub">Both models score <b>0/10</b>: Qwen3-8B sits below Terminal-Bench's task floor, so this axis
detects no quality difference at 8B scale. The trials are still instructive to read. Three failure families
repeat in both arms: declaring the task done after a shallow first attempt, shell quoting errors that prevent
files from ever being written, and looping on analysis until the 45-minute timeout. Expand any step to read
the agent's own commentary (harbor terminus-2, temperature 0, pinned task list).</div>
{''.join(blocks)}
</body></html>"""
    (SITE / "compare_coding.html").write_text(page)
    print(f"wrote compare_coding.html ({len(page)//1024} KB, {len(TASKS)} tasks)")


if __name__ == "__main__":
    main()
