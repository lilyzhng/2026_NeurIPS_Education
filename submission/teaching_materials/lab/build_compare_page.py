#!/usr/bin/env python3
"""Side-by-side comparison: vanilla vs DFlash frontend outputs, LIVE.

Each cell embeds the actual generated page in an iframe (hover and click work),
with a Code toggle showing the source. Scores from scores.json under each cell.
Writes local/draft_v2/demo/compare_frontend.html; serve the demo dir and open.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "local/draft_v2/data/4_6_radar_pilot"
OUT = ROOT / "local/draft_v2/demo/compare_frontend.html"

BRIEFS = {
    "od673": "Stunning translucent calendar popup that smoothly blends into the interface.",
    "od5": "Create a user interface for a life insurance website.",
    "od6": "Landing page selling dog-related products.",
    "od8": "Revamped Airbnb homepage for group adventures.",
    "od9": "Mobile application for vehicle loans and financing on iOS devices.",
    "od10": "Homepage for an animation studio, Studio Ghibli inspired.",
    "od340": "Photo card interface, hover triggers a gentle 3D flip effect.",
    "od341": "Newsletter registration pop-up, soothing hues, smartphone optimized.",
}


def src_for(arm: str, oid: str) -> str:
    if oid == "od673":
        return f"{arm}_raw.html"
    return f"radar/{arm}_frontend_{oid}.html"


def main() -> None:
    scores = json.loads((D / "scores_opendesign.json").read_text())
    cells, rows = [], []
    idx = 0
    for oid, brief in BRIEFS.items():
        pair = []
        for arm, label in [("vanilla", "vanilla"), ("dflash", "DFlash")]:
            page = ROOT / "local/draft_v2/demo" / src_for(arm, oid)
            if not page.exists():
                pair = []
                break
            s = scores.get(arm, {}).get(oid, {})
            sc = (f"OpenDesign judge {s.get('total_score','?')}/100 &middot; "
                  f"align {s.get('alignment_score','?')}/40 "
                  f"aes {s.get('aesthetics_score','?')}/30 "
                  f"struct {s.get('structure_score','?')}/30"
                  if s else "not judged")
            pair.append(f'''<div class="cell">
  <div class="head"><b>{label}</b><span class="sc">{sc}</span>
    <button class="tgl" onclick="toggle({idx})" id="t{idx}">Code</button></div>
  <iframe id="f{idx}" src="{src_for(arm, oid)}" loading="lazy"></iframe>
  <pre id="p{idx}" style="display:none"></pre>
</div>''')
            idx += 1
        if pair:
            rows.append(f'<div class="brief"><b>{oid}</b> &middot; {brief}</div>'
                        f'<div class="pair">{"".join(pair)}</div>')

    OUT.write_text(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>vanilla vs DFlash: live frontend outputs</title>
<style>
  body {{ margin:0; padding:24px; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; color:#222; }}
  h1 {{ font-size:20px; }} .sub {{ color:#666; font-size:13px; margin-bottom:8px; }}
  .brief {{ margin:28px 0 8px; font-size:14px; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .cell {{ border:1px solid #ddd; border-radius:10px; overflow:hidden; background:#fff; }}
  .cell .head {{ display:flex; gap:10px; align-items:center; padding:6px 10px; font-size:13px;
                 background:#1e2a1c; color:#fff; }}
  .cell .sc {{ margin-left:auto; font-size:12px; color:#b9c7b2; }}
  .tgl {{ font-size:11px; padding:2px 10px; border-radius:8px; border:1px solid #667;
          background:#2b3a28; color:#fff; cursor:pointer; }}
  .cell iframe {{ width:100%; height:480px; border:0; display:block; background:#fff; }}
  .cell pre {{ height:480px; overflow:auto; margin:0; padding:10px 12px; background:#1e2a1c;
               color:#e8e8e3; font-size:10.5px; line-height:1.45; white-space:pre-wrap;
               word-break:break-word; }}
</style></head><body>
<h1>Same brief, two deployments: vanilla Qwen3-8B (left) vs + DFlash draft (right)</h1>
<div class="sub">Live pages, interact directly (hover, click). Greedy decoding, so every difference is trajectory divergence. Scores use OpenDesign's official GPT-4o judge prompt: alignment with instruction /40, aesthetics and readability /30, structural integrity /30, total /100.</div>
{''.join(rows)}
<script>
async function toggle(i) {{
  const f = document.getElementById('f'+i), p = document.getElementById('p'+i),
        t = document.getElementById('t'+i);
  const showCode = p.style.display === 'none';
  if (showCode && !p.textContent) p.textContent = await (await fetch(f.src)).text();
  f.style.display = showCode ? 'none' : 'block';
  p.style.display = showCode ? 'block' : 'none';
  t.textContent = showCode ? 'Render' : 'Code';
}}
</script>
</body></html>""")
    print("wrote", OUT, "| rows:", len(rows))


if __name__ == "__main__":
    main()
