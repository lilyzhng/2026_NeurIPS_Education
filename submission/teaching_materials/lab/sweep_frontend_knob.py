#!/usr/bin/env python3
"""Knob demo v2: sweep the acceptance threshold on the frontend task (od673).

For each threshold: redeploy the DSpark server with ACCEPT_THRESHOLD, generate
the od673 calendar-popup page at temperature 0, save the raw HTML, and record
tokens/s + accept length + line-diff vs the strict (1.0) page.

Greedy decoding is the point: at threshold 1.0 the output must match the
vanilla page byte-for-byte, so any diff below 1.0 is attributable to the knob.
If every stop comes back byte-identical, rerun with --temperature 1 (thresholds
bite harder when sampling) before concluding the knob is inert here.

  python3 sweep_frontend_knob.py --url https://<you>--neurips-lab-sglang-serve.modal.run
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

THRESHOLDS = ["1.0", "0.9", "0.7", "0.5", "0.3", "0.1"]

# Same brief as generate_frontend_task.py (OpenDesign id 673).
PROMPT = (
    "You are a frontend engineer. Produce a complete single-file HTML page "
    "(inline CSS, no external assets) for the following brief. Output only the "
    "HTML, starting with <!DOCTYPE html>.\n\n"
    "Brief: Stunning translucent calendar popup that smoothly blends into the "
    "interface."
)


def _post(url: str, payload: dict, timeout: int = 900) -> dict:
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
            return
        except Exception:  # noqa: BLE001
            time.sleep(15)
    raise SystemExit("server not ready")


def accept_length(base: str) -> float | None:
    try:
        m = re.findall(r"spec_accept_length\S*\s+([0-9.eE+-]+)", _get(f"{base}/metrics"))
        return float(m[-1]) if m else None
    except Exception:  # noqa: BLE001
        return None


def redeploy(threshold: str, script_dir: Path) -> None:
    env = {"SPEC_MODE": "dspark", "ACCEPT_THRESHOLD": threshold}
    print(f"[deploy] threshold={threshold}", flush=True)
    subprocess.run(
        ["uvx", "--with", "modal", "modal", "deploy", "modal_sglang_serve.py"],
        cwd=script_dir, check=True, env={**__import__("os").environ, **env},
        capture_output=True,
    )
    time.sleep(20)  # let the old container drain


def diff_stats(strict: str, other: str) -> dict:
    a, b = strict.splitlines(), other.splitlines()
    changed = sum(1 for d in difflib.ndiff(a, b) if d[:1] in "+-")
    ratio = difflib.SequenceMatcher(None, strict, other).ratio()
    return {"identical": strict == other,
            "diff_lines": changed,
            "char_similarity": round(ratio, 4)}


def run(base: str, out_dir: Path, max_tokens: int, temperature: float) -> None:
    script_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    metaf = out_dir / "meta.json"
    data = json.loads(metaf.read_text()) if metaf.exists() else {}
    for th in THRESHOLDS:
        redeploy(th, script_dir)
        wait_ready(base)
        _post(f"{base}/v1/completions", {"model": "default", "prompt": "warmup",
                                         "max_tokens": 16, "temperature": 0})
        t0 = time.time()
        resp = _post(f"{base}/v1/chat/completions", {
            "model": "default",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": max_tokens, "temperature": temperature,
            "chat_template_kwargs": {"enable_thinking": False},
        })
        dt = time.time() - t0
        text = resp["choices"][0]["message"]["content"]
        (out_dir / f"th_{th}.html").write_text(text)
        toks = resp.get("usage", {}).get("completion_tokens", 0)
        data[th] = {
            "seconds": round(dt, 1),
            "completion_tokens": toks,
            "tokens_per_s": round(toks / dt, 1) if dt else None,
            "accept_length": accept_length(base),
        }
        if "1.0" in data and th != "1.0":
            strict = (out_dir / "th_1.0.html").read_text()
            data[th].update(diff_stats(strict, text))
        metaf.write_text(json.dumps(data, indent=1))  # incremental save per threshold
        print(f"[th={th}] {data[th]}", flush=True)
    print(json.dumps(data, indent=1))
    # stop the serve app so the GPU is released (scripted stop needs -y)
    subprocess.run(["uvx", "--with", "modal", "modal", "app", "stop", "-y",
                    "neurips-lab-sglang"], check=False)
    print("[cleanup] modal app stop issued")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--max-tokens", type=int, default=3000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3]
                                         / "local/draft_v2/data/4_3_knob_frontend"))
    a = ap.parse_args()
    run(a.url.rstrip("/"), Path(a.out), a.max_tokens, a.temperature)
