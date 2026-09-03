#!/usr/bin/env python3
"""Build creative_race_demo.html: 2x2 live race on the L073 creative prompt.

Same layout as build_race_demo.py, but the payoff is length: each pane streams
1000 words of prose at its lane's measured speed, then flips to a typeset
reading view. Reads texts + speeds from local/draft_v2/data/4_5_creative/.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "local/draft_v2/data/4_5_creative"
OUT = ROOT / "local/draft_v2/demo/creative_race_demo.html"

LANES = [("vanilla", "vanilla"), ("eagle3", "EAGLE-3"),
         ("dflash", "DFlash"), ("dspark", "DSpark")]

PROMPT_HTML = (
    "Prompt (LosslessBench L073, EQ-Bench Creative Writing v3): Historical "
    "Fiction. Write a scene from a story set during the height of the Roman "
    "Empire, a slice of a day in the life of a gladiator. No combat scene. "
    "Sensory details, the gladiator's thoughts, the politics of the time. "
    "<b>First person, past tense, 1000 words.</b>"
)


def js_str(t: str) -> str:
    return json.dumps(t).replace("</", "<\\/")


def main() -> None:
    meta = json.loads((DATA / "meta.json").read_text())
    texts, speeds, names = [], [], []
    for key, name in LANES:
        texts.append((DATA / f"{key}.md").read_text())
        speeds.append(meta[key]["tokens_per_s"])
        names.append(name)

    panes = "\n".join(
        f'''  <div class="pane"><div class="head">
    <span>{names[i]}</span><span class="stats" id="s{i}">0.0s &middot; 0 tok</span>
    <button class="tgl" id="t{i}" onclick="toggle({i})" disabled>Read</button></div>
    <pre id="p{i}"></pre><div class="story" id="f{i}" style="display:none"></div>
    <div class="badge" id="b{i}"></div></div>'''
        for i in range(4))

    page = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>The decoding race: 1000 words</title>
<style>
  body { margin:0; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; }
  .grid { display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:8px; padding:8px; height:calc(100vh - 48px); box-sizing:border-box; }
  .pane { position:relative; border:1px solid #ddd; border-radius:10px; background:#1e2a1c; display:flex; flex-direction:column; min-height:0; overflow:hidden; }
  .badge { display:none; position:absolute; right:10px; bottom:10px; background:rgba(20,28,18,.92); color:#fff;
           border:1px solid #4a5a44; border-radius:12px; padding:6px 12px; text-align:right; box-shadow:0 4px 14px rgba(0,0,0,.35); z-index:2; }
  .badge .big { font-size:22px; font-weight:800; line-height:1; font-variant-numeric:tabular-nums; }
  .badge .sub { font-size:11px; color:#cfd8c8; margin-top:3px; }
  .head { padding:6px 10px; font-size:13px; font-weight:600; color:#fff; display:flex; gap:10px; align-items:center; }
  .head .stats { margin-left:auto; font-weight:400; font-size:12px; color:#b9c7b2; font-variant-numeric:tabular-nums; }
  .tgl { font-size:11px; padding:2px 10px; border-radius:8px; border:1px solid #667; background:#2b3a28; color:#fff; cursor:pointer; }
  .tgl:disabled { opacity:.35; cursor:default; }
  pre { flex:1; margin:0; padding:8px 12px; overflow-y:auto; font-family:ui-monospace,monospace; font-size:11px;
        line-height:1.5; color:#e8e8e3; white-space:pre-wrap; word-break:break-word; min-height:0; }
  .story { flex:1; overflow-y:auto; min-height:0; padding:14px 18px; }
  .story .sheet { max-width:520px; margin:0 auto; background:#f7f4ec; border-radius:6px; padding:26px 30px;
                  font-family:Georgia,'Times New Roman',serif; font-size:12.5px; line-height:1.65; color:#2b2b26;
                  box-shadow:0 6px 20px rgba(0,0,0,.35); }
  .story .sheet h2 { font-size:16px; margin:0 0 14px; }
  .story .sheet p { margin:0 0 12px; }
  .bar { height:36px; display:flex; align-items:center; justify-content:center; gap:12px; }
  button.replay { font-size:13px; padding:5px 16px; border-radius:8px; border:1px solid #bbb; background:#fff; cursor:pointer; }
  .note { font-size:12px; color:#666; }
</style></head><body>
<div class="grid">
__PANES__
</div>
<div class="bar"><button class="replay" onclick="run()">&#9654; Replay</button></div>
<script>
const T = __TEXTS__;
const TPS = __SPEEDS__;
let timers = [];
function storyHtml(s) {
  const cut = s.lastIndexOf('<\\/think>');
  if (cut >= 0) s = s.slice(cut + 8);
  const esc = s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const paras = esc.split(/\\n\\s*\\n/).filter(p => p.trim());
  let out = '';
  for (const p of paras) {
    const t = p.trim();
    if (t.startsWith('#')) out += '<h2>' + t.replace(/^#+\\s*/,'') + '</h2>';
    else out += '<p>' + t.replace(/\\n/g,' ') + '</p>';
  }
  return '<div class="sheet">' + out + '</div>';
}
function laneSecs(i) { return (T[i].length/4)/TPS[i]; }
function fillBadge(i) {
  const secs = laneSecs(i);
  const fastest = [0,1,2,3].every(j => laneSecs(i) <= laneSecs(j));
  document.getElementById('b'+i).innerHTML =
    '<div class="big">' + (fastest ? '&#127942; ' : '') + secs.toFixed(1) + 's</div>' +
    '<div class="sub">' + TPS[i].toFixed(0) + ' tok/s · ' + Math.round(T[i].length/4) + ' tok</div>';
}
function showRead(i, on) {
  document.getElementById('p'+i).style.display = on ? 'none' : 'block';
  const f = document.getElementById('f'+i); f.style.display = on ? 'block' : 'none';
  if (on && !f.innerHTML) f.innerHTML = storyHtml(T[i]);
  if (on) fillBadge(i);
  document.getElementById('b'+i).style.display = on ? 'block' : 'none';
  document.getElementById('t'+i).textContent = on ? 'Raw' : 'Read';
}
function toggle(i) { showRead(i, document.getElementById('f'+i).style.display === 'none'); }
function run() {
  timers.forEach(clearInterval); timers = [];
  [0,1,2,3].forEach(i => {
    const pre = document.getElementById('p'+i), st = document.getElementById('s'+i), tg = document.getElementById('t'+i);
    document.getElementById('f'+i).innerHTML = ''; showRead(i, false);
    tg.disabled = true; pre.textContent = ''; const cps = TPS[i]*4; const t0 = performance.now();
    const iv = setInterval(() => {
      const el = (performance.now()-t0)/1000;
      const pos = Math.min(T[i].length, Math.round(el*cps));
      pre.textContent = T[i].slice(0,pos); pre.scrollTop = pre.scrollHeight;
      st.textContent = el.toFixed(1)+'s \\u00b7 '+Math.round(pos/4)+' tok'+(pos>=T[i].length?' \\u00b7 done':'');
      if (pos >= T[i].length) { clearInterval(iv); tg.disabled = false; setTimeout(()=>showRead(i,true), 700); }
    }, 50);
    timers.push(iv);
  });
}
function showFinal() {
  [0,1,2,3].forEach(i => {
    const secs = (T[i].length/4)/TPS[i];
    document.getElementById('s'+i).textContent = secs.toFixed(1)+'s · '+Math.round(T[i].length/4)+' tok · done';
    document.getElementById('t'+i).disabled = false;
    showRead(i, true);
  });
}
window.addEventListener('load', showFinal);
</script></body></html>"""
    page = page.replace("__PROMPT__", PROMPT_HTML)
    page = page.replace("__PANES__", panes)
    page = page.replace("__TEXTS__", "[" + ",".join(js_str(t) for t in texts) + "]")
    page = page.replace("__SPEEDS__", json.dumps(speeds))
    OUT.write_text(page)
    print("wrote", OUT, "| lanes:", list(zip(names, speeds)))


if __name__ == "__main__":
    main()
