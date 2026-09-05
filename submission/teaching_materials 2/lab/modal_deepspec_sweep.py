#!/usr/bin/env python3
"""Section 4.3 threshold sweep on the DeepSpec eval harness (Modal, one H100).

DSpark's confidence threshold is a DeepSpec-harness knob, not an SGLang flag,
so this sweep runs DeepSpec's own eval.py inside a Modal function.

Probe the harness flags first (cheap, no GPU work):
  modal run modal_deepspec_sweep.py::probe

Then sweep (gsm8k subset, one eval per threshold; answers kept for grading):
  modal run modal_deepspec_sweep.py::sweep

Results land in the `neurips-lab-out` volume under /out/sweep/<threshold>/,
download with: modal volume get neurips-lab-out sweep ./data/sweep
"""
from __future__ import annotations

import subprocess

import modal

MINUTES = 60
TARGET = "Qwen/Qwen3-8B"
DRAFT = "deepseek-ai/dspark_qwen3_8b_block7"
THRESHOLDS = [1.0, 0.9, 0.7, 0.5, 0.3]

hf_cache = modal.Volume.from_name("qwen3-8b-hf-cache", create_if_missing=True)
out_vol = modal.Volume.from_name("neurips-lab-out", create_if_missing=True)

image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .apt_install("git", "curl", "build-essential", "ca-certificates")
    .pip_install("torch", "transformers", "accelerate", "datasets", "huggingface_hub")
    .run_commands("git clone https://github.com/deepseek-ai/DeepSpec /root/DeepSpec",
                  "pip install -e /root/DeepSpec || pip install -r /root/DeepSpec/requirements.txt || true")
    .env({"HF_HOME": "/root/.cache/huggingface"})
)

app = modal.App("neurips-lab-deepspec-sweep")


@app.function(image=image, gpu="H100", timeout=15 * MINUTES,
              volumes={"/root/.cache/huggingface": hf_cache})
def probe() -> None:
    """Print eval.py's actual flags so the sweep call below can be pinned."""
    for cmd in (["python3", "/root/DeepSpec/scripts/eval/eval.py", "--help"],
                ["ls", "/root/DeepSpec/scripts/eval"]):
        print("$", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=False)


@app.function(image=image, gpu="H100", timeout=120 * MINUTES,
              volumes={"/root/.cache/huggingface": hf_cache, "/out": out_vol})
def sweep(benchmark: str = "gsm8k", limit: int = 50) -> None:
    """One eval per threshold. Flag names verified via probe() before first run."""
    for th in THRESHOLDS:
        outdir = f"/out/sweep/{th}"
        cmd = [
            "python3", "/root/DeepSpec/scripts/eval/eval.py",
            "--target-model", TARGET,
            "--draft-checkpoint", DRAFT,
            "--benchmark", benchmark,
            "--limit", str(limit),
            "--confidence-threshold", str(th),
            "--save-generations", outdir,
        ]
        print("$", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, check=False)
        print(f"[sweep th={th}] exit={r.returncode}", flush=True)
        out_vol.commit()  # incremental save per threshold
