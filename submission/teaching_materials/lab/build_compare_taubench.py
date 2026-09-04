#!/usr/bin/env python3
"""Build compare_taubench.html: left/right tau3 A/B viewer (vanilla vs DFlash).

Reads local/draft_v2/data/4_6_radar_pilot/agent_results/{vanilla,dflash}_results.json
+ win_counts.json + the retail task definitions, renders every paired episode as
side-by-side agent traces with the full scoring breakdown (DB match, action
checks, NL assertions) in the compare_frontend.html design language.

  python3 build_compare_taubench.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
DATA = ROOT / "local/draft_v2/data/4_6_radar_pilot/agent_results"
OUT = ROOT / "local/draft_v2/demo/compare_taubench.html"
TASKS = Path.home() / "Documents/projects/tau2-bench/data/tau2/domains/retail/tasks.json"


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def load(arm: str) -> dict:
    d = json.loads((DATA / f"{arm}_results.json").read_text())
    return {s["task_id"]: s for s in d["simulations"]}


def render_trace(sim: dict) -> str:
    rows = []
    for m in sim.get("messages") or []:
        role = m.get("role")
        content = m.get("content") or ""
        if role == "assistant":
            think, reply = "", content
            if "<think>" in content:
                pre, _, rest = content.partition("<think>")
                think, _, post = rest.partition("</think>")
                reply = (pre + post).strip()
            if think.strip():
                rows.append(
                    f'<details class="think"><summary>&#129504; thinking '
                    f"({len(think.split())} words)</summary><div>{esc(think.strip())}</div></details>"
                )
            if reply:
                rows.append(f'<div class="msg agent"><b>agent</b>{esc(reply)}</div>')
            for tc in m.get("tool_calls") or []:
                name, args = tc.get("name"), json.dumps(tc.get("arguments"), ensure_ascii=False)
                cls = "write" if any(k in (name or "") for k in ("exchange", "return", "modify", "cancel")) else "read"
                rows.append(f'<div class="tool {cls}">&#128295; <b>{esc(name)}</b>({esc(args)})</div>')
        elif role == "user":
            rows.append(f'<div class="msg user"><b>user</b>{esc(content)}</div>')
        elif role == "tool":
            short = content if len(str(content)) < 160 else str(content)[:160] + " …"
            rows.append(
                f'<details class="tres"><summary>&#8618; result: {esc(short)}</summary>'
                f"<div>{esc(content)}</div></details>"
            )
    return "\n".join(rows)


def render_detail(sim: dict) -> str:
    ri = sim.get("reward_info") or {}
    reward = ri.get("reward")
    dbc = ri.get("db_check") or {}
    acs = ri.get("action_checks") or []
    nl = ri.get("nl_assertions") or []
    rb = ri.get("reward_breakdown") or {}
    ok = sum(1 for a in acs if a.get("action_match"))
    parts = []
    passed = (reward or 0) > 0
    head_cls = "fb" if passed else "fb bad0"
    db_txt = "&#10003; DB state matches gold" if dbc.get("db_match") else "&#10007; final DB state &ne; gold state"
    parts.append(
        f'<div class="{head_cls}">reward <b>{reward}</b> &middot; {db_txt} &middot; '
        f"gold actions {ok}/{len(acs)} &middot; breakdown {esc(json.dumps(rb)) if rb else 'n/a'} "
        f"&middot; term: {esc(sim.get('termination_reason'))}</div>"
    )
    items = []
    for a in acs:
        act = a.get("action") or {}
        args = json.dumps(act.get("arguments"), ensure_ascii=False)
        mark = "match" if a.get("action_match") else "MISS"
        cls = "" if a.get("action_match") else ' class="bad"'
        sym = "&#10003;" if a.get("action_match") else "&#10007;"
        items.append(
            f"<li{cls} title=\"{esc(args)}\">{sym} {mark} <b>{esc(act.get('name'))}</b> "
            f'<span class="tt">[{esc(a.get("tool_type"))}]</span></li>'
        )
    for n in nl:
        okn = n.get("met", n.get("passed"))
        cls = "" if okn else ' class="bad"'
        sym = "&#10003;" if okn else "&#10007;"
        items.append(f"<li{cls}>{sym} NL: {esc(n.get('nl_assertion') or n)}</li>")
    return parts[0] + "<ul>" + "".join(items) + "</ul>"


def main() -> None:
    van, dfl = load("vanilla"), load("dflash")
    wc = json.loads((DATA / "win_counts.json").read_text())
    tasks = {t["id"]: t for t in json.loads(TASKS.read_text())}

    blocks = []
    for tid in wc["task_ids"]:
        purpose = ""
        t = tasks.get(tid) or {}
        scen = ((t.get("user_scenario") or {}).get("instructions") or {})
        purpose = (scen.get("task_instructions") or scen.get("reason_for_call") or "")[:220]
        cells = []
        rv = (van[tid].get("reward_info") or {}).get("reward") or 0
        rd = (dfl[tid].get("reward_info") or {}).get("reward") or 0
        for arm, sim, r, other in (("vanilla", van[tid], rv, rd), ("DFlash", dfl[tid], rd, rv)):
            badge = ""
            if r > other:
                badge = '<span class="wbadge">&#127942; winner</span>'
            elif r > 0 and r == other:
                badge = '<span class="wbadge tie">&#10003; both pass</span>'
            cells.append(
                f'<div class="cell"><div class="head"><b>{arm}</b>'
                f'<span class="sc">reward {r}</span>{badge}</div>'
                f'<div class="trace">{render_trace(sim)}</div>'
                f'<div class="detail">{render_detail(sim)}</div></div>'
            )
        blocks.append(
            f'<div class="brief"><b>task {tid}</b> &middot; {esc(purpose)}</div>'
            f'<div class="pair">{cells[0]}{cells[1]}</div>'
        )

    criteria = """
<details class="crit" open><summary><b>Judging criteria &amp; scoring mechanism</b> (click to fold)</summary>
<ul>
<li><b>Judge = tau2-bench's own reward function.</b> No LLM judge of ours. An episode scores <b>1.0</b> only if every component in its reward basis passes; otherwise 0.</li>
<li><b>DB check</b>: after the conversation, the environment database (orders, payments, items) must exactly match the gold final state. Doing nothing, or doing extra writes, both fail this.</li>
<li><b>Action checks</b>: the gold action sequence (lookups + the write that executes the transaction). Each is matched by name + arguments against what the agent actually called.</li>
<li><b>NL assertions</b> (where defined): facts the agent must have communicated, checked by GPT-4.1 at temp 0.</li>
<li><b>Controls</b>: identical 10 retail tasks both arms, agent temp 0, user simulator gpt-4o temp 0, seed 300, branch fix/ab-scoring-artifacts.</li>
<li><b>Win rule (2026-09-03)</b>: per task, higher reward wins; both-pass = one point each; <b>both-fail = zero points</b> (win count therefore equals pass count). Result: <b>vanilla 2/10, DFlash 3/10</b>; only task 8 separates the arms. At n=10 this is within noise.</li>
</ul></details>"""

    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>tau3 retail: vanilla Qwen3-8B vs + DFlash draft</title>
<style>
  body {{ margin:0; padding:24px; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; color:#222; }}
  h1 {{ font-size:20px; }} .sub {{ color:#666; font-size:13px; margin-bottom:8px; }}
  .crit {{ background:#fff; border:1px solid #ddd; border-radius:10px; padding:10px 14px; font-size:13px; margin:14px 0; }}
  .crit li {{ margin:4px 0; }}
  .brief {{ margin:28px 0 8px; font-size:14px; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .cell {{ border:1px solid #ddd; border-radius:10px; overflow:hidden; background:#fff; }}
  .cell .head {{ display:flex; gap:10px; align-items:center; padding:6px 10px; font-size:13px;
                 background:#1e2a1c; color:#fff; }}
  .cell .sc {{ font-size:12px; color:#b9c7b2; }}
  .wbadge {{ background:#c9a227; color:#1e2a1c; padding:1px 8px; border-radius:8px; font-size:11px; font-weight:700; margin-left:auto; }}
  .wbadge.tie {{ background:#7a9b76; color:#fff; }}
  .trace {{ height:420px; overflow-y:auto; padding:10px 12px; font-size:12px; line-height:1.5; background:#fbfbf9; }}
  .msg {{ margin:6px 0; padding:6px 9px; border-radius:8px; white-space:pre-wrap; word-break:break-word; }}
  .msg b {{ display:block; font-size:10px; text-transform:uppercase; letter-spacing:.4px; opacity:.55; margin-bottom:2px; }}
  .msg.user {{ background:#eef2ff; border:1px solid #dfe6ff; }}
  .msg.agent {{ background:#f0f6ef; border:1px solid #e0ebdf; }}
  .tool {{ font-family:ui-monospace,Menlo,monospace; font-size:11px; margin:4px 0 4px 14px; padding:4px 8px;
           border-left:3px solid #8aa; background:#f4f7f7; border-radius:0 6px 6px 0; word-break:break-all; }}
  .tool.write {{ border-left-color:#c9a227; background:#fdf8ea; }}
  details.think, details.tres {{ margin:2px 0 2px 14px; font-size:11px; color:#777; }}
  details.think > div, details.tres > div {{ white-space:pre-wrap; background:#f4f4f2; border-radius:6px; padding:6px 8px; margin-top:3px; max-height:180px; overflow-y:auto; }}
  details summary {{ cursor:pointer; }}
  .detail {{ padding:8px 12px; font-size:12px; border-top:1px solid #eee; height:150px; overflow-y:auto; }}
  .detail .fb {{ color:#2c5f2d; margin-bottom:4px; }}
  .detail .fb.bad0 {{ color:#a33; }}
  .detail ul {{ margin:0; padding-left:2px; list-style:none; }}
  .detail li {{ margin:2px 0; color:#2c5f2d; }}
  .detail li.bad {{ color:#a33; cursor:help; }}
  .detail .tt {{ color:#999; font-size:10px; }}
</style></head><body>
<h1>tau3 retail: vanilla Qwen3-8B (left) vs + DFlash draft (right)</h1>
<div class="sub"><b>Pass count: vanilla 2/10 &middot; DFlash 3/10</b> &middot; 10 tasks, both arms, agent temp 0, user sim gpt-4o temp 0. Both-fail scores zero (rule 2026-09-03). Full traces below &mdash; &#128295; = tool call (gold border = state-changing write), fold-outs = model thinking / tool results.</div>
{criteria}
{''.join(blocks)}
</body></html>"""
    OUT.write_text(page)
    print(f"wrote {OUT} ({len(page)//1024} KB)")


if __name__ == "__main__":
    main()
