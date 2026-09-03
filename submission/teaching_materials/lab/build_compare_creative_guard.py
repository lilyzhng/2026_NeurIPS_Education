#!/usr/bin/env python3
"""Comparison pages for the other two pilot domains.

compare_creative.html   5 briefs (L073-L077), typeset story left/right,
                        GPT-4o rubric scores, winner badge per row
compare_guardrail.html  5 XSTest prompts, labels vs gold, flip column
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "local/draft_v2/data/4_6_radar_pilot"
LB = Path.home() / "Documents/lily-memory/Build/LosslessBench"

CSS = """
  body { margin:0; padding:24px; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; color:#222; }
  h1 { font-size:20px; } .sub { color:#666; font-size:13px; margin-bottom:8px; }
  .brief { margin:28px 0 8px; font-size:14px; }
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .cell { border:1px solid #ddd; border-radius:10px; overflow:hidden; background:#fff; }
  .cell .head { display:flex; gap:10px; align-items:center; padding:6px 10px; font-size:13px;
                background:#1e2a1c; color:#fff; white-space:nowrap; overflow:hidden; }
  .cell .sc { font-size:12px; color:#b9c7b2; }
  .wbadge { background:#c9a227; color:#1e2a1c; padding:1px 8px; border-radius:8px; font-size:11px; font-weight:700; }
  .story { height:420px; overflow-y:auto; padding:16px 20px; font-family:Georgia,serif;
           font-size:13px; line-height:1.6; color:#2b2b26; background:#f9f7f1; }
  .story p { margin:0 0 10px; }
  table { border-collapse:collapse; width:100%; margin-top:16px; }
  th, td { text-align:left; padding:8px 10px; border-bottom:1px solid #ddd; font-size:13px; vertical-align:top; }
  .ok { color:#2c5f2d; } .err { color:#a33; font-weight:600; }
  .detail { padding:8px 12px; font-size:12px; border-top:1px solid #eee; height:190px; overflow-y:auto; }
  .detail ul { margin:0 0 6px; padding-left:2px; list-style:none; }
  .detail li.good { color:#2c5f2d; margin:2px 0; }
  .detail li.bad { color:#a33; margin:2px 0; }
  .analysis { color:#555; border-top:1px dashed #ddd; padding-top:6px; }
"""


def story_html(text: str) -> str:
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{html.escape(p)}</p>" for p in paras)


def creative() -> None:
    eq = json.loads((D / "scores_eqbench_cw3.json").read_text())
    neg = set(eq["_negative_criteria"])
    briefs = {}
    for lid in ["L073", "L074", "L075", "L076", "L077"]:
        t = json.loads((LB / f"lossless100/hydrated/tasks/{lid}/task.json").read_text())
        briefs[lid] = t["prompt"].replace("<SEED>", "").strip()[:160]
    rows, wins = [], {"vanilla": 0, "dflash": 0}
    for lid, brief in briefs.items():
        sv, sd = eq["vanilla"][lid], eq["dflash"][lid]
        if sv["eqbench_score_0_20"] == sd["eqbench_score_0_20"]:
            wins["vanilla"] += 1; wins["dflash"] += 1   # tie: one point each
            winner = None
        else:
            winner = "vanilla" if sv["eqbench_score_0_20"] > sd["eqbench_score_0_20"] else "dflash"
            wins[winner] += 1
        cells = []
        for arm, label, sc in [("vanilla", "vanilla", sv), ("dflash", "DFlash", sd)]:
            text = (D / arm / f"creative_{lid}.txt").read_text()
            # effective score per criterion (negatives inverted), best and worst
            eff = sorted(((20 - v if c in neg else v), c, v) for c, v in sc["criteria"].items())
            worst = [f'<li class="bad">&#10007; {c} {v:.0f}/20'
                     f'{" (lower is better)" if c in neg else ""}</li>' for e, c, v in eff[:3]]
            best = [f'<li class="good">&#10003; {c} {v:.0f}/20</li>' for e, c, v in reversed(eff[-3:])]
            badge = '<span class="wbadge">&#127942; winner</span>' if arm == winner else ""
            cells.append(
                f'<div class="cell"><div class="head"><b>{label}</b>'
                f'<span class="sc">EQ-Bench {sc["eqbench_score_0_20"]}/20</span>{badge}</div>'
                f'<div class="story">{story_html(text)}</div>'
                f'<div class="detail"><ul>{"".join(best)}{"".join(worst)}</ul>'
                f'<div class="analysis">{html.escape(sc["analysis"])}</div></div></div>')
        rows.append(f'<div class="brief"><b>{lid}</b> &middot; {html.escape(brief)}...</div>'
                    f'<div class="pair">{"".join(cells)}</div>')
    out = ROOT / "local/draft_v2/demo/compare_creative.html"
    crits = ", ".join(c for c in eq["vanilla"]["L073"]["criteria"])
    out.write_text(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>vanilla Qwen3-8B vs + DFlash draft: creative</title>
<style>{CSS}</style></head><body>
<h1>vanilla Qwen3-8B (left) vs + DFlash draft (right): creative writing</h1>
<div class="sub">Win count: vanilla {wins['vanilla']}, DFlash {wins['dflash']} (a tie scores one point for each side).</div>
<div class="sub"><b>Judging</b>: EQ-Bench Creative Writing v3 official rubric, GPT-4o judge, 22 criteria scored 0-20, negative criteria inverted. Green = top strengths, red = weakest criteria; full judge analysis below each.</div>
{''.join(rows)}
</body></html>""")
    print("wrote", out, "| wins:", wins)


def guardrail() -> None:
    import csv
    prompts = {f"xs{r['id']}": r["prompt"]
               for r in csv.DictReader(open(LB / "data_guard/xstest_prompts.csv"))}
    metas = {arm: json.loads((D / arm / "meta.json").read_text()) for arm in ["vanilla", "dflash"]}

    def label(arm, key):
        t = (D / arm / f"{key}.txt").read_text()
        if "</think>" in t:
            t = t.split("</think>")[-1]
        hits = re.findall(r"\b(safe|unsafe)\b", t, re.I)
        return hits[-1].lower() if hits else "none"

    trs = []
    correct = {"vanilla": 0, "dflash": 0}
    n = 0
    for key, v in metas["vanilla"].items():
        if "gold" not in v:
            continue
        gold = v["gold"]
        lv, ld = label("vanilla", key), label("dflash", key)
        n += 1
        correct["vanilla"] += lv == gold
        correct["dflash"] += ld == gold
        def cell(l):
            cls = "ok" if l == gold else "err"
            return f'<td class="{cls}">{l}{"" if l == gold else " &#10007;"}</td>'
        trs.append(f'<tr><td>{html.escape(prompts[key.split("_")[1]])}</td>'
                   f'<td>{gold}</td>{cell(lv)}{cell(ld)}</tr>')
    out = ROOT / "local/draft_v2/demo/compare_guardrail.html"
    out.write_text(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>vanilla Qwen3-8B vs + DFlash draft: guardrail</title>
<style>{CSS}</style></head><body>
<h1>vanilla Qwen3-8B (left) vs + DFlash draft (right): guardrail (XSTest)</h1>
<div class="sub">Score: vanilla {correct["vanilla"]}/{n}, DFlash {correct["dflash"]}/{n}. Wrong labels marked &#10007;.</div>
<table><tr><th>prompt</th><th>gold</th><th>vanilla</th><th>DFlash</th></tr>
{''.join(trs)}</table>
</body></html>""")
    print("wrote", out, "| correct:", correct)


if __name__ == "__main__":
    creative()
    guardrail()
