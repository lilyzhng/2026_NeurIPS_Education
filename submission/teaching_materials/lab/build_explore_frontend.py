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
  body {{ margin:0; padding:14px 18px 18px; font-family:'ET Book', Palatino, Georgia, serif;
         background:#fffffb; color:#111; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }}
  .chip {{ font-size:13px; padding:4px 12px; border-radius:999px; border:1px solid #d8d8d0;
           background:#fff; cursor:pointer; font-family:inherit; }}
  .chip:hover {{ border-color:#1f5c3d; }}
  .chip.on {{ background:#1f5c3d; color:#fff; border-color:#1f5c3d; }}
  .brief {{ font-size:15px; font-style:italic; color:#444; margin:2px 0 12px; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
  .cell {{ border:1px solid #e2e2da; border-radius:12px; overflow:hidden; background:#fff;
           box-shadow:0 1px 4px rgba(0,0,0,.04); }}
  .head {{ display:flex; gap:10px; align-items:baseline; padding:9px 14px 7px; }}
  .head b {{ font-size:15px; }}
  .head .v {{ color:#1f5c3d; }} .head .p {{ color:#d6437c; }}
  .total {{ font-size:13px; color:#666; }}
  .wbadge {{ margin-left:auto; font-size:11px; letter-spacing:.5px; font-weight:700;
             color:#8a6d1a; background:#f7edd2; border:1px solid #e3cf94;
             padding:2px 10px; border-radius:999px; align-self:center;
             font-family:-apple-system,sans-serif; }}
  .meters {{ display:flex; gap:14px; padding:0 14px 8px; }}
  .m {{ flex:1; }}
  .m .lab {{ font-size:11px; color:#888; letter-spacing:.3px; margin-bottom:2px;
             font-family:-apple-system,sans-serif; }}
  .m .bar {{ height:6px; border-radius:3px; background:#eeeee6; overflow:hidden; }}
  .m .fill {{ height:100%; border-radius:3px; }}
  .cell.van .fill {{ background:#1f5c3d; }} .cell.dfl .fill {{ background:#d6437c; }}
  iframe {{ width:100%; height:500px; border:0; border-top:1px solid #eee; display:block; background:#fff; }}
  .fb {{ padding:10px 14px 12px; font-size:13.5px; line-height:1.5; color:#3a3a36;
         border-top:1px solid #f0f0e8; min-height:66px; }}
</style></head><body>
<div class="chips" id="chips"></div>
<div class="brief" id="brief"></div>
<div class="pair">
  <div class="cell van"><div class="head"><b class="v">vanilla Qwen3-8B</b><span class="total" id="s0"></span><span class="wbadge" id="w0" style="display:none">WINNER</span></div>
    <div class="meters"><div class="m"><div class="lab">CODE <span id="c0"></span>/40</div><div class="bar"><div class="fill" id="cb0"></div></div></div>
    <div class="m"><div class="lab">FUNCTIONALITY <span id="u0"></span>/60</div><div class="bar"><div class="fill" id="ub0"></div></div></div></div>
    <iframe id="f0"></iframe><div class="fb" id="d0"></div></div>
  <div class="cell dfl"><div class="head"><b class="p">+ DFlash draft</b><span class="total" id="s1"></span><span class="wbadge" id="w1" style="display:none">WINNER</span></div>
    <div class="meters"><div class="m"><div class="lab">CODE <span id="c1"></span>/40</div><div class="bar"><div class="fill" id="cb1"></div></div></div>
    <div class="m"><div class="lab">FUNCTIONALITY <span id="u1"></span>/60</div><div class="bar"><div class="fill" id="ub1"></div></div></div></div>
    <iframe id="f1"></iframe><div class="fb" id="d1"></div></div>
</div>
<script>
const DATA = {json.dumps(data)};
const chips = document.getElementById('chips');
Object.keys(DATA).forEach((t, i) => {{
  const b = document.createElement('button');
  b.className = 'chip'; b.textContent = t; b.onclick = () => show(t);
  chips.appendChild(b);
}});
function show(t) {{
  const d = DATA[t];
  [...chips.children].forEach(c => c.classList.toggle('on', c.textContent === t));
  document.getElementById('brief').textContent = '\u201C' + d.brief + '\u201D';
  [d.vanilla, d.dflash].forEach((a, i) => {{
    document.getElementById('f'+i).src = 'explore/' + a.file;
    document.getElementById('s'+i).textContent = 'total ' + a.total + ' / 100';
    document.getElementById('c'+i).textContent = a.code;
    document.getElementById('u'+i).textContent = a.func;
    document.getElementById('cb'+i).style.width = (a.code/40*100) + '%';
    document.getElementById('ub'+i).style.width = (a.func/60*100) + '%';
    document.getElementById('d'+i).textContent = a.feedback;
  }});
  document.getElementById('w0').style.display = d.vanilla.total > d.dflash.total ? '' : 'none';
  document.getElementById('w1').style.display = d.dflash.total > d.vanilla.total ? '' : 'none';
}}
show('od673');
</script>
</body></html>"""
    (SITE / "explore_frontend.html").write_text(page)
    print(f"wrote explore_frontend.html + {len(data)} task pairs -> {OUT_DIR}")


if __name__ == "__main__":
    main()
