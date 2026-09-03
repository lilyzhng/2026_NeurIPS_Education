#!/usr/bin/env python3
"""Modal SGLang server for the Section 4 hands-on lab.

Serves Qwen/Qwen3-8B on one H100, with or without the DeepSpec EAGLE-3 speculator.

Deploy vanilla (baseline):
  SPEC_MODE=vanilla uvx --with modal modal deploy modal_sglang_serve.py

Deploy with speculative decoding:
  SPEC_MODE=eagle3 uvx --with modal modal deploy modal_sglang_serve.py

Smoke:
  curl -L https://lilyzhng--neurips-lab-sglang-serve.modal.run/health

Stop when done (the server holds the GPU until stopped):
  uvx --with modal modal app stop neurips-lab-sglang
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import modal

# vanilla | eagle3 | dflash | dspark
SPEC_MODE = os.environ.get("SPEC_MODE", "vanilla").strip().lower()
TARGET_MODEL = os.environ.get("TARGET_MODEL", "Qwen/Qwen3-8B")
DRAFTS = {
    "eagle3": "deepseek-ai/eagle3_qwen3_8b_ttt7",
    "dflash": "deepseek-ai/dflash_qwen3_8b_block7",
    "dspark": "deepseek-ai/dspark_qwen3_8b_block7",
}
DRAFT_MODEL = os.environ.get("DRAFT_MODEL", DRAFTS.get(SPEC_MODE, DRAFTS["eagle3"]))
# 4.3 knob: relaxed acceptance. 1.0 = strict (lossless); lower = accept more draft tokens.
ACCEPT_THRESHOLD = os.environ.get("ACCEPT_THRESHOLD", "1.0")
PORT = 30000
MINUTES = 60

hf_cache = modal.Volume.from_name("qwen3-8b-hf-cache", create_if_missing=True)


def _load_hf_token() -> str | None:
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    envfile = Path("/Users/lilyzhang/Documents/lily-memory/GeniusTeam/genius-builder/.env")
    if envfile.is_file():
        for line in envfile.read_text().splitlines():
            if line.startswith("HF_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


_hf_token = _load_hf_token()
_secrets = [modal.Secret.from_dict({"HF_TOKEN": _hf_token})] if _hf_token else []

sglang_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .apt_install("git", "curl", "build-essential", "ca-certificates", "libnuma1")
    .pip_install("sglang[all]>=0.5", "huggingface_hub")
    .env(
        {
            "HF_HOME": "/root/.cache/huggingface",
            "CUDA_HOME": "/usr/local/cuda",
            "PATH": "/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "SPEC_MODE": SPEC_MODE,
            "TARGET_MODEL": TARGET_MODEL,
            "DRAFT_MODEL": DRAFT_MODEL,
            "ACCEPT_THRESHOLD": ACCEPT_THRESHOLD,
        }
    )
)

app = modal.App("neurips-lab-sglang")


def _build_cmd() -> list[str]:
    mode = os.environ.get("SPEC_MODE", SPEC_MODE).strip().lower()
    target = os.environ.get("TARGET_MODEL", TARGET_MODEL)
    cmd = [
        "python3", "-m", "sglang.launch_server",
        "--model-path", target,
        "--host", "0.0.0.0",
        "--port", str(PORT),
        "--mem-fraction-static", "0.85",
        "--enable-metrics",
    ]
    draft = os.environ.get("DRAFT_MODEL", DRAFTS.get(mode, ""))
    if mode == "eagle3":
        cmd += [
            "--speculative-algorithm", "EAGLE3",
            "--speculative-draft-model-path", draft,
            "--speculative-num-steps", "3",
            "--speculative-eagle-topk", "4",
            "--speculative-num-draft-tokens", "16",
        ]
    th = os.environ.get("ACCEPT_THRESHOLD", ACCEPT_THRESHOLD)
    if mode != "vanilla" and th != "1.0":
        cmd += ["--speculative-accept-threshold-single", th,
                "--speculative-accept-threshold-acc", th]
    if mode in ("dflash", "dspark"):
        # Both natively supported by SGLang. Note: of the DeepSpec checkpoints only
        # dspark loads here (dflash ships markov_rank=0; use z-lab drafters for DFLASH).
        cmd += [
            "--speculative-algorithm", mode.upper(),
            "--speculative-draft-model-path", draft,
        ]
    elif mode != "vanilla":
        raise ValueError(f"unknown SPEC_MODE={mode!r} (vanilla|eagle3|dflash|dspark)")
    print(f"[sglang] mode={mode} target={target}", flush=True)
    print(" ".join(cmd), flush=True)
    return cmd


@app.function(
    image=sglang_image,
    gpu="H100",
    min_containers=1,
    max_containers=1,
    timeout=60 * MINUTES,
    scaledown_window=10 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=_secrets,
)
@modal.web_server(port=PORT, startup_timeout=15 * MINUTES)
def serve():
    subprocess.Popen(_build_cmd())
