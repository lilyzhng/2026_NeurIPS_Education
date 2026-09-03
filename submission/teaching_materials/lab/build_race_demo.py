#!/usr/bin/env python3
"""Build race_demo.html: 2x2 live race (vanilla / EAGLE-3 / DFlash / DSpark).

Each pane streams its lane's REAL generated code at the lane's measured tok/s,
scrolling inside the box. When a lane finishes, its pane flips to a rendered
preview of the page it just wrote (iframe srcdoc), with a Code/Render toggle.

Reads texts + speeds from local/draft_v2/data/4_4_frontend/. Rerun after any
lane's generate_frontend_task.py run to refresh.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "local/draft_v2/data/4_4_frontend"
OUT = ROOT / "local/draft_v2/demo/race_demo.html"

# 2x2 order: top-left, top-right, bottom-left, bottom-right
LANES = [
    ("vanilla", "vanilla", "#8a4a2b"),
    ("eagle3", "EAGLE-3", "#39598c"),
    ("dflash", "DFlash", "#97662a"),
    ("dspark", "DSpark", "#2c5f2d"),
]


def js_str(t: str) -> str:
    return json.dumps(t).replace("</", "<\\/")


def load_lane(label: str) -> tuple[str, float]:
    meta = json.loads((DATA / "meta.json").read_text())
    s = (DATA / f"{label}.html").read_text()
    i = s.rfind("<!DOCTYPE")
    return (s[i:] if i > 0 else s), meta[label]["tokens_per_s"]


def main() -> None:
    texts, speeds, names, colors = [], [], [], []
    for key, name, color in LANES:
        t, tps = load_lane(key)
        texts.append(t)
        speeds.append(tps)
        names.append(name)
        colors.append(color)

    panes = "\n".join(
        f'''  <div class="pane"><div class="head">
    <span>{names[i]}</span><span class="stats" id="s{i}">0.0s &middot; 0 tok</span>
    <button class="tgl" id="t{i}" onclick="toggle({i})" disabled>Render</button></div>
    <pre id="p{i}"></pre><div class="rwrap" id="w{i}" style="display:none"><iframe id="f{i}"></iframe></div>
    <div class="badge" id="b{i}"></div></div>'''
        for i in range(4))

    page = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>The decoding race, live</title>
<style>
  body { margin:0; font-family:-apple-system,'Inter',sans-serif; background:#faf9f7; }
  .grid { display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:8px; padding:8px; height:calc(100vh - 48px); box-sizing:border-box; }
  .pane { position:relative; border:1px solid #ddd; border-radius:10px; background:#1e2a1c; display:flex; flex-direction:column; min-height:0; overflow:hidden; }
  .badge { display:none; position:absolute; right:10px; bottom:10px; background:rgba(20,28,18,.92); color:#fff;
           border:1px solid #4a5a44; border-radius:12px; padding:6px 12px; text-align:right; box-shadow:0 4px 14px rgba(0,0,0,.35); }
  .badge .big { font-size:22px; font-weight:800; line-height:1; font-variant-numeric:tabular-nums; }
  .badge .sub { font-size:11px; color:#cfd8c8; margin-top:3px; }
  .head { padding:6px 10px; font-size:13px; font-weight:600; color:#fff; display:flex; gap:10px; align-items:center; }
  .head .stats { margin-left:auto; font-weight:400; font-size:12px; color:#b9c7b2; font-variant-numeric:tabular-nums; }
  .tgl { font-size:11px; padding:2px 10px; border-radius:8px; border:1px solid #667; background:#2b3a28; color:#fff; cursor:pointer; }
  .tgl:disabled { opacity:.35; cursor:default; }
  pre { flex:1; margin:0; padding:8px 10px; overflow-y:auto; font-family:ui-monospace,monospace; font-size:10.5px;
        line-height:1.4; color:#e8e8e3; white-space:pre-wrap; word-break:break-word; min-height:0; }
  .rwrap { flex:1; position:relative; min-height:0; overflow:hidden; }
  .rwrap iframe { position:absolute; top:0; left:0; width:200%; height:200%; border:0; background:#1e2a1c;
                  transform:scale(.5); transform-origin:0 0; }
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
function extractDoc(s) {
  const i = s.indexOf('<!DOCTYPE'); const j = s.lastIndexOf('<\\/html>');
  let doc = i>=0 ? s.slice(i, j>i ? j+7 : s.length) : s;
  // the generated pages hide the calendar behind a button; open it so the render is visible
  const opener = '<scr'+'ipt>window.addEventListener("load",()=>{setTimeout(()=>{const b=document.querySelector("button"); if(b) b.click();},300);});</scr'+'ipt>'
    + '<style>html,body{background:#1e2a1c !important;} body>*{background-color:transparent !important;}</style>';
  return doc.replace(/<\\/body>/i, opener+'<\\/body>');
}
function laneSecs(i) { return (T[i].length/4)/TPS[i]; }
function fillBadge(i) {
  const secs = laneSecs(i);
  const fastest = [0,1,2,3].every(j => laneSecs(i) <= laneSecs(j));
  document.getElementById('b'+i).innerHTML =
    '<div class="big">' + (fastest ? '&#127942; ' : '') + secs.toFixed(1) + 's</div>' +
    '<div class="sub">' + TPS[i].toFixed(0) + ' tok/s \u00b7 ' + Math.round(T[i].length/4) + ' tok</div>';
}
function showRender(i, on) {
  document.getElementById('p'+i).style.display = on ? 'none' : 'block';
  document.getElementById('w'+i).style.display = on ? 'block' : 'none';
  const f = document.getElementById('f'+i);
  if (on && !f.srcdoc) f.srcdoc = extractDoc(T[i]);
  if (on) fillBadge(i);
  document.getElementById('b'+i).style.display = on ? 'block' : 'none';
  document.getElementById('t'+i).textContent = on ? 'Code' : 'Render';
}
function toggle(i) { showRender(i, document.getElementById('w'+i).style.display === 'none'); }
function run() {
  timers.forEach(clearInterval); timers = [];
  [0,1,2,3].forEach(i => {
    const pre = document.getElementById('p'+i), st = document.getElementById('s'+i), tg = document.getElementById('t'+i);
    const f = document.getElementById('f'+i); f.removeAttribute('srcdoc'); showRender(i, false);
    tg.disabled = true; pre.textContent = ''; const cps = TPS[i]*4; const t0 = performance.now();
    const iv = setInterval(() => {
      const el = (performance.now()-t0)/1000;
      const pos = Math.min(T[i].length, Math.round(el*cps));
      pre.textContent = T[i].slice(0,pos); pre.scrollTop = pre.scrollHeight;
      st.textContent = el.toFixed(1)+'s \\u00b7 '+Math.round(pos/4)+' tok'+(pos>=T[i].length?' \\u00b7 done':'');
      if (pos >= T[i].length) { clearInterval(iv); tg.disabled = false; setTimeout(()=>showRender(i,true), 700); }
    }, 50);
    timers.push(iv);
  });
}
function showFinal() {
  [0,1,2,3].forEach(i => {
    const secs = (T[i].length/4)/TPS[i];
    document.getElementById('s'+i).textContent = secs.toFixed(1)+'s \u00b7 '+Math.round(T[i].length/4)+' tok \u00b7 done';
    document.getElementById('t'+i).disabled = false;
    showRender(i, true);
  });
}
window.addEventListener('load', showFinal);
</script></body></html>"""
    page = page.replace("__PANES__", panes)
    page = page.replace("__TEXTS__", "[" + ",".join(js_str(t) for t in texts) + "]")
    page = page.replace("__SPEEDS__", json.dumps(speeds))
    OUT.write_text(page)
    print("wrote", OUT, "| lanes:", list(zip(names, speeds)))


if __name__ == "__main__":
    main()
