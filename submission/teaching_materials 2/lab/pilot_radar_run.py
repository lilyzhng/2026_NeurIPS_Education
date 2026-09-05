#!/usr/bin/env python3
"""Run the 15 radar-pilot prompts against a served arm (vanilla lane).

  python3 pilot_radar_run.py --url https://<you>--neurips-spec-lab-vanilla-serve.modal.run --arm vanilla

Greedy. Saves one file per item plus meta into
local/draft_v2/data/4_6_radar_pilot/<arm>/.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path

from pilot_radar_prompts import build, build_hard, build_round2

ROOT = Path(__file__).resolve().parents[3]


def run(base: str, arm: str, mode: str = "base") -> None:
    out_dir = ROOT / f"local/draft_v2/data/4_6_radar_pilot/{arm}"
    out_dir.mkdir(parents=True, exist_ok=True)
    # burn warmup on a throwaway (failures.md R9: first request pays compile)
    _post(base, {"model": "default", "max_tokens": 16, "temperature": 0,
                 "messages": [{"role": "user", "content": "Say hi."}]})
    metaf = out_dir / "meta.json"
    meta = json.loads(metaf.read_text()) if metaf.exists() else {}
    items = {"base": build, "hard": build_hard, "round2": build_round2}[mode]()
    for it in items:
        if (out_dir / f"{it['domain']}_{it['id']}.txt").exists():
            print(f"[{arm}] skip {it['domain']}_{it['id']} (exists)", flush=True)
            continue
        t0 = time.time()
        resp = _post(base, {"model": "default", "temperature": 0,
                            "max_tokens": it["max_tokens"], "messages": it["messages"]})
        dt = time.time() - t0
        text = resp["choices"][0]["message"]["content"]
        tokens = resp.get("usage", {}).get("completion_tokens", 0)
        (out_dir / f"{it['domain']}_{it['id']}.txt").write_text(text)
        meta[f"{it['domain']}_{it['id']}"] = {
            "seconds": round(dt, 1), "completion_tokens": tokens,
            "tokens_per_s": round(tokens / dt, 1) if dt else 0,
            **({"gold": it["gold"]} if "gold" in it else {})}
        print(f"[{arm}] {it['domain']}_{it['id']}: {tokens} tok in {dt:.1f}s", flush=True)
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=1))


def _post(base: str, payload: dict) -> dict:
    req = urllib.request.Request(f"{base}/v1/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--mode", default="base", choices=["base", "hard", "round2"])
    a = ap.parse_args()
    run(a.url.rstrip("/"), a.arm, a.mode)
