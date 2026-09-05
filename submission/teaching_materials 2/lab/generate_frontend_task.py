#!/usr/bin/env python3
"""Section 4.4: generate the Figure 11 frontend task (OpenDesign id 673) on one lane.

Greedy decoding, so a lossless speculator must reproduce the vanilla HTML
byte-for-byte. The diff (or its absence) is the experiment.

  python3 generate_frontend_task.py --url <server> --label vanilla
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path

PROMPT = (
    "You are a frontend engineer. Produce a complete single-file HTML page "
    "(inline CSS, no external assets) for the following brief. Output only the "
    "HTML, starting with <!DOCTYPE html>.\n\n"
    "Brief: Stunning translucent calendar popup that smoothly blends into the "
    "interface."
)


def run(base: str, label: str, out_dir: Path, max_tokens: int, suffix: str = ".html") -> None:
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=json.dumps({"model": "default",
                         "messages": [{"role": "user", "content": PROMPT}],
                         "max_tokens": max_tokens, "temperature": 0}).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.loads(r.read())
    dt = time.time() - t0
    text = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{label}{suffix}").write_text(text)
    meta = {"label": label, "seconds": round(dt, 1),
            "completion_tokens": usage.get("completion_tokens"),
            "tokens_per_s": round(usage.get("completion_tokens", 0) / dt, 1)}
    metaf = out_dir / "meta.json"
    data = json.loads(metaf.read_text()) if metaf.exists() else {}
    data[label] = meta
    metaf.write_text(json.dumps(data, indent=1))
    print(f"[{label}] {meta}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3]
                                         / "local/draft_v2/data/4_4_frontend"))
    a = ap.parse_args()
    run(a.url.rstrip("/"), a.label, Path(a.out), a.max_tokens)
