#!/usr/bin/env python3
"""Modal vLLM server for the Section 4 hands-on lab.

Serves Qwen/Qwen3-8B on one H100 with DeepSpec speculators. All draft weights
come from the DeepSpec release (same training data and settings across
algorithms), so cross-algorithm comparisons stay controlled.

  SPEC_MODE=vanilla uvx --with modal modal deploy modal_vllm_serve.py
  SPEC_MODE=eagle3  uvx --with modal modal deploy modal_vllm_serve.py
  SPEC_MODE=dflash  uvx --with modal modal deploy modal_vllm_serve.py
  SPEC_MODE=dspark  uvx --with modal modal deploy modal_vllm_serve.py

Stop when done (the server holds the GPU until stopped):
  uvx --with modal modal app stop neurips-spec-lab
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import modal

SPEC_MODE = os.environ.get("SPEC_MODE", "vanilla").strip().lower()
TARGET_MODEL = os.environ.get("TARGET_MODEL", "Qwen/Qwen3-8B")
DRAFTS = {
    "eagle3": "deepseek-ai/eagle3_qwen3_8b_ttt7",
    "dflash": "z-lab/Qwen3-8B-DFlash-b16",  # vLLM e2e acceptance-test recipe
    "dspark": "deepseek-ai/dspark_qwen3_8b_block7",
}
NUM_SPEC_TOKENS = {"eagle3": "3", "dflash": "16", "dspark": "7"}  # dflash b16 per vLLM e2e test
DRAFT_MODEL = os.environ.get("DRAFT_MODEL", DRAFTS.get(SPEC_MODE, ""))
PORT = 8000
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

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .apt_install("git", "curl", "build-essential", "ca-certificates", "libnuma1")
    .pip_install(
        *(["vllm", "huggingface_hub"] if os.environ.get("VLLM_NIGHTLY") != "1"
          else ["huggingface_hub"]),
    )
    .run_commands(
        "pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly"
        if os.environ.get("VLLM_NIGHTLY") == "1" else "true"
    )
    .env(
        {
            "HF_HOME": "/root/.cache/huggingface",
            "CUDA_HOME": "/usr/local/cuda",
            "PATH": "/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "VLLM_USE_FLASHINFER_SAMPLER": "0",
            "SPEC_MODE": SPEC_MODE,
            "TARGET_MODEL": TARGET_MODEL,
            "DRAFT_MODEL": DRAFT_MODEL,
        }
    )
)

# APP_NAME lets two lanes run on separate GPUs in parallel (e.g. neurips-spec-lab-b).
app = modal.App(os.environ.get("APP_NAME", "neurips-spec-lab"))


def _build_cmd() -> list[str]:
    mode = os.environ.get("SPEC_MODE", SPEC_MODE).strip().lower()
    target = os.environ.get("TARGET_MODEL", TARGET_MODEL)
    cmd = [
        "vllm", "serve", target,
        "--host", "0.0.0.0",
        "--port", str(PORT),
        "--served-model-name", "default",
        "--max-model-len", "8192",
        "--gpu-memory-utilization", "0.90",
    ]
    if os.environ.get("ENFORCE_EAGER") == "1":
        cmd += ["--enforce-eager"]
    if mode != "vanilla":
        if mode not in DRAFTS:
            raise ValueError(f"unknown SPEC_MODE={mode!r} (vanilla|eagle3|dflash|dspark)")
        draft = os.environ.get("DRAFT_MODEL", DRAFTS[mode])
        spec = {"model": draft, "method": mode,
                "num_speculative_tokens": int(NUM_SPEC_TOKENS[mode])}
        cmd += ["--speculative-config", json.dumps(spec)]
    print(f"[vllm] mode={mode} target={target}", flush=True)
    print(" ".join(cmd), flush=True)
    return cmd


@app.function(
    image=vllm_image,
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
    cmd = _build_cmd()
    mode = os.environ.get("SPEC_MODE", SPEC_MODE).strip().lower()
    if mode == "eagle3":
        # DeepSpec's eagle3 fuses FIVE target layers (fc is [4096, 5*4096]); vLLM
        # defaults to 3 unless the draft config names the aux layers. Patch it in.
        from huggingface_hub import snapshot_download

        draft = os.environ.get("DRAFT_MODEL", DRAFTS["eagle3"])
        local = snapshot_download(draft)
        cfg_path = f"{local}/config.json"
        cfg = json.load(open(cfg_path))
        cfg["architectures"] = ["Eagle3Qwen3ForCausalLM"]  # stable vLLM's Qwen3 eagle3 class
        cfg["eagle_aux_hidden_state_layer_ids"] = [1, 9, 17, 25, 33]
        cfg["num_aux_layers"] = 5
        json.dump(cfg, open(cfg_path, "w"), indent=1)
        print(f"[patch] {draft}: arch -> Eagle3Qwen3ForCausalLM, aux 5 layers", flush=True)
        i = cmd.index("--speculative-config") + 1
        spec = json.loads(cmd[i])
        spec["model"] = local
        cmd[i] = json.dumps(spec)
    if mode == "dflash":
        # DeepSpec's dflash checkpoint carries the DSpark arch tag; vLLM's dflash
        # path expects DFlashDraftModel (both are in vLLM's registry). Relabel.
        from huggingface_hub import snapshot_download

        draft = os.environ.get("DRAFT_MODEL", DRAFTS["dflash"])
        local = snapshot_download(draft)
        cfg_path = f"{local}/config.json"
        cfg = json.load(open(cfg_path))
        if "deepseek-ai" in draft and ("dflash_config" not in cfg or cfg.get("architectures") != ["DFlashDraftModel"]):
            cfg["architectures"] = ["DFlashDraftModel"]
            # vLLM reads these via the nested dflash_config (z-lab layout);
            # DeepSpec ships them flat at top level, so re-wrap them.
            cfg["dflash_config"] = {
                "mask_token_id": cfg.get("mask_token_id", 151669),
                "target_layer_ids": cfg.get("target_layer_ids", [1, 9, 17, 25, 33]),
            }
            json.dump(cfg, open(cfg_path, "w"), indent=1)
            print(f"[patch] {draft}: arch relabel + nested dflash_config", flush=True)
        i = cmd.index("--speculative-config") + 1
        spec = json.loads(cmd[i])
        spec["model"] = local
        cmd[i] = json.dumps(spec)
    subprocess.Popen(cmd)
