#!/usr/bin/env python3
"""Section 4.2 race bench: one algorithm at a time, three prompt domains.

Same measurement core as measure_decoding_speed.py, but the prompt set is split into
coding / creative / frontend so per-domain acceptance (τ) is visible.
Run once per deployed SPEC_MODE; results accumulate in 4_2_race.json.

Usage (after `SPEC_MODE=eagle3 modal deploy modal_sglang_serve.py`):
  python3 race_domains.py --url https://<you>--neurips-lab-sglang-serve.modal.run --label eagle3
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

DOMAINS = {
    "coding": (
        "Write a Python function that parses an Apache access log line into a dict "
        "with fields ip, timestamp, method, path, status, bytes. Include type hints "
        "and a short docstring, then show three usage examples."
    ),
    "creative": (
        "Write the opening scene of a short story about a lighthouse keeper who "
        "receives a letter from someone who claims to be her future self. "
        "Plain conversational prose, several paragraphs."
    ),
    "frontend": (
        "Write a single-file HTML page with embedded CSS for a personal reading-list "
        "app: a header, a two-column card grid, and a floating add button. "
        "Modern, minimal styling."
    ),
}


def _post(url: str, payload: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get(url: str, timeout: int = 30) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode()


def wait_ready(base: str, wait_s: int = 900) -> None:
    deadline = time.time() + wait_s
    while time.time() < deadline:
        try:
            _get(f"{base}/health", timeout=10)
            print("[ready]")
            return
        except Exception as e:  # noqa: BLE001
            print(f"[wait] {type(e).__name__}; retry 15s", flush=True)
            time.sleep(15)
    raise SystemExit("server not ready")


def accept_length(base: str) -> float | None:
    try:
        text = _get(f"{base}/metrics")
    except Exception:  # noqa: BLE001
        return None
    m = re.findall(r"spec_accept_length\S*\s+([0-9.eE+-]+)", text)
    return float(m[-1]) if m else None


def run(base: str, label: str, runs: int, max_tokens: int, out: Path) -> None:
    wait_ready(base)
    _post(f"{base}/v1/completions", {"model": "default", "prompt": "warmup",
                                     "max_tokens": 32, "temperature": 0})
    data = json.loads(out.read_text()) if out.exists() else {}
    entry = data.setdefault(label, {})
    for domain, prompt in DOMAINS.items():
        tau_before = accept_length(base)
        recs = []
        for i in range(runs):
            t0 = time.time()
            resp = _post(f"{base}/v1/completions", {
                "model": "default", "prompt": prompt,
                "max_tokens": max_tokens, "temperature": 0,
            })
            dt = time.time() - t0
            ctok = resp.get("usage", {}).get("completion_tokens")
            recs.append({"seconds": round(dt, 2), "completion_tokens": ctok,
                         "tokens_per_s": round(ctok / dt, 1) if ctok else None})
            print(f"[{label}/{domain}] run {i}: {recs[-1]}", flush=True)
        entry[domain] = {"runs": recs,
                         "tau_cumulative_after": accept_length(base),
                         "tau_cumulative_before": tau_before}
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=1))  # incremental save per domain
    med = {d: sorted(r["tokens_per_s"] for r in entry[d]["runs"])[len(entry[d]["runs"]) // 2]
           for d in DOMAINS}
    print(f"[{label}] medians tok/s: {med}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--label", required=True, help="vanilla|eagle3|dflash|dspark")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3]
                                         / "local/draft_v2/data/4_2_race.json"))
    a = ap.parse_args()
    run(a.url.rstrip("/"), a.label, a.runs, a.max_tokens, Path(a.out))
