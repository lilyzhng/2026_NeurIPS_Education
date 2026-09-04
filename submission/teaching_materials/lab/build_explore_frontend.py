#!/usr/bin/env python3
"""Build explore_frontend.html: dropdown task explorer for the interactive site.

Reuses the recorded frontend outputs (11 OpenDesign tasks, both arms) and the
interactive-judge scores. Copies the per-task renders into
interactive_site/explore/ and emits a selector page with side-by-side iframes
plus each arm's score and judge feedback.

  python3 build_explore_frontend.py
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
DEMO = ROOT / "local/draft_v2/demo"
SITE = ROOT / "submission/teaching_materials/interactive_site"
OUT_DIR = SITE / "explore"
SCORES = ROOT / "local/draft_v2/data/4_6_radar_pilot/scores_interactive.json"

BRIEFS = {
    "od673": "Stunning translucent calendar popup that smoothly blends into the interface.",
    "od5": "Create a user interface for a life insurance website.",
    "od6": "Landing page selling dog-related products.",
    "od8": "Revamped Airbnb homepage for group adventures.",
    "od9": "Mobile application for vehicle loans and financing on iOS devices.",
    "od10": "Homepage for an animation studio, Studio Ghibli inspired.",
    "od11": "A user interface that resembles Spotify, focusing on music navigation and playlists.",
    "od20": "A template to display traffic data using interactive charts and graphs.",
    "od28": "Interactive charts showcasing trading trends and accident statistics in New York.",
    "od340": "Photo card interface, hover triggers a gentle 3D flip effect.",
    "od341": "Newsletter registration pop-up, soothing hues, smartphone optimized.",
}


def src_for(task: str, arm: str) -> Path:
    if task == "od673":
        return DEMO / ("vanilla_raw.html" if arm == "vanilla" else "dflash_raw.html")
    return DEMO / "radar" / f"{arm}_frontend_{task}.html"


def main() -> None:
    scores = json.loads(SCORES.read_text())
    OUT_DIR.mkdir(exist_ok=True)
    data = {}
    for task, brief in BRIEFS.items():
        entry = {"brief": brief}
        for arm in ("vanilla", "dflash"):
            src = src_for(task, arm)
            if not src.is_file():
                continue
            dst = OUT_DIR / f"{arm}_{task}.html"
            shutil.copy(src, dst)
            s = scores.get(arm, {}).get(task) or {}
            entry[arm] = {
                "file": dst.name,
                "total": s.get("total"),
                "code": s.get("code_correctness"),
                "func": s.get("functionality"),
                "feedback": s.get("feedback", ""),
            }
        if "vanilla" in entry and "dflash" in entry:
            data[task] = entry

    options = "".join(
        f'<option value="{t}">{t} · {html.escape(d["brief"][:70])}</option>'
        for t, d in data.items()
    )
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Explore the frontend tasks</title>
<style>
  body {{ margin:0; padding:18px 24px; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; color:#222; }}
  .bar {{ display:flex; gap:12px; align-items:center; margin-bottom:10px; flex-wrap:wrap; }}
  select {{ font-size:14px; padding:6px 10px; border-radius:8px; border:1px solid #ccc; max-width:560px; }}
  .verdict {{ font-size:13px; color:#555; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .cell {{ border:1px solid #ddd; border-radius:10px; overflow:hidden; background:#fff; }}
  .head {{ display:flex; gap:10px; align-items:center; padding:6px 10px; font-size:13px; background:#1e2a1c; color:#fff; }}
  .sc {{ font-size:12px; color:#b9c7b2; }}
  .wbadge {{ background:#c9a227; color:#1e2a1c; padding:1px 8px; border-radius:8px; font-size:11px; font-weight:700; margin-left:auto; }}
  iframe {{ width:100%; height:520px; border:0; display:block; background:#fff; }}
  .fb {{ padding:8px 12px; font-size:12px; color:#444; border-top:1px solid #eee; min-height:60px; }}
</style></head><body>
<div class="bar">
  <b>Pick a task:</b>
  <select id="sel" onchange="show(this.value)">{options}</select>
  <span class="verdict" id="verdict"></span>
</div>
<div class="pair">
  <div class="cell"><div class="head"><b>vanilla</b><span class="sc" id="s0"></span><span class="wbadge" id="w0" style="display:none">WINNER</span></div>
    <iframe id="f0"></iframe><div class="fb" id="d0"></div></div>
  <div class="cell"><div class="head"><b>+ DFlash draft</b><span class="sc" id="s1"></span><span class="wbadge" id="w1" style="display:none">WINNER</span></div>
    <iframe id="f1"></iframe><div class="fb" id="d1"></div></div>
</div>
<script>
const DATA = {json.dumps(data)};
function show(t) {{
  const d = DATA[t];
  document.getElementById('verdict').textContent = d.brief;
  const arms = [d.vanilla, d.dflash];
  arms.forEach((a, i) => {{
    document.getElementById('f'+i).src = 'explore/' + a.file;
    document.getElementById('s'+i).textContent = 'total ' + a.total + ' (code ' + a.code + '/40, functionality ' + a.func + '/60)';
    document.getElementById('d'+i).textContent = a.feedback;
  }});
  document.getElementById('w0').style.display = d.vanilla.total > d.dflash.total ? '' : 'none';
  document.getElementById('w1').style.display = d.dflash.total > d.vanilla.total ? '' : 'none';
}}
show(document.getElementById('sel').value);
</script>
</body></html>"""
    (SITE / "explore_frontend.html").write_text(page)
    print(f"wrote explore_frontend.html + {len(data)} task pairs -> {OUT_DIR}")


if __name__ == "__main__":
    main()
