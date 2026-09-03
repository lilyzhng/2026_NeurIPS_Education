#!/usr/bin/env python3
"""Section 4.1 bench: measure decode tokens/s (and acceptance length when speculative).

Stdlib only. Waits for the server, runs N timed generations of the same prompt,
scrapes /metrics for the speculative accept length, and appends results to a JSON file.

Usage:
  python3 bench_41.py --url https://lilyzhng--neurips-lab-sglang-serve.modal.run \
      --label vanilla --out ../../..//local/draft_v2/data/4_1_bench.json
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

# Figure 1's sentence: the bench continues conversational text in the same spirit.
PROMPT = (
    "Continue this passage in plain conversational prose for several paragraphs: "
    '"It does not do to dwell on dreams and forget to live."'
)


def _post(url: str, payload: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
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
            print("[ready] /health 200")
            return
        except Exception as e:  # noqa: BLE001
            print(f"[wait] {type(e).__name__}: {e}; retrying in 15s", flush=True)
            time.sleep(15)
    raise SystemExit(f"server not ready after {wait_s}s")


def accept_length(base: str) -> float | None:
    """Scrape the speculative accept length from Prometheus /metrics, if exposed."""
    try:
        text = _get(f"{base}/metrics")
    except Exception:  # noqa: BLE001
        return None
    # sglang exposes e.g. sglang:spec_accept_length{...} <value>
    m = re.findall(r"spec_accept_length\S*\s+([0-9.eE+-]+)", text)
    return float(m[-1]) if m else None


def run(base: str, label: str, runs: int, max_tokens: int, out: Path) -> None:
    wait_ready(base)
    # one warmup (not recorded): first request pays compile/caching cost
    _post(f"{base}/v1/completions", {
        "model": "default", "prompt": PROMPT, "max_tokens": 64, "temperature": 0,
    })
    results = []
    for i in range(runs):
        t0 = time.time()
        resp = _post(f"{base}/v1/completions", {
            "model": "default", "prompt": PROMPT,
            "max_tokens": max_tokens, "temperature": 0,
        })
        dt = time.time() - t0
        ctok = resp.get("usage", {}).get("completion_tokens")
        toks = ctok / dt if ctok else None
        rec = {"run": i, "seconds": round(dt, 2), "completion_tokens": ctok,
               "tokens_per_s": round(toks, 1) if toks else None}
        results.append(rec)
        print(f"[{label}] run {i}: {rec}", flush=True)
        # incremental save after every run
        _save(out, label, results, accept_length(base))
    print(f"[{label}] done. median tok/s = "
          f"{sorted(r['tokens_per_s'] for r in results)[len(results)//2]}")


def _save(out: Path, label: str, results: list, tau: float | None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(out.read_text()) if out.exists() else {}
    data[label] = {"runs": results, "spec_accept_length": tau,
                   "prompt": PROMPT, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out.write_text(json.dumps(data, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--label", required=True, help="vanilla | eagle3")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3]
                                         / "local/draft_v2/data/4_1_bench.json"))
    a = ap.parse_args()
    run(a.url.rstrip("/"), a.label, a.runs, a.max_tokens, Path(a.out))
