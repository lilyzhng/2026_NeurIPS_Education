#!/usr/bin/env python3
"""Per-domain acceptance rate / acceptance length for DFlash — ORIGINAL tasks only.

Groups (5 prompts each):
  gsm8k_paper       HF openai/gsm8k test split, first 5   (DFlash Table 1 benchmark)
  humaneval_paper   HF openai/openai_humaneval, first 5   (DFlash Table 1 benchmark)
  agentic_coding    lossless100 hydrated L035-L039        (LosslessBench Coding)
  front_end_design  lossless100 L098-L101 + OpenDesign od5 (LosslessBench Frontend)
  creative_writing  lossless100 hydrated L088-L092        (LosslessBench Writing)

For each prompt we snapshot vLLM's cumulative spec-decode counters
before/after generation; the delta gives that prompt's acceptance stats.

  alpha = accepted_draft_tokens / proposed_draft_tokens   (Theorem 3.5: 1 - D_LK)
  tau   = accepted/drafts + 1 (bonus token)

temperature=1, Qwen3 thinking mode disabled (matching DFlash Table 1 temp=1 rows).

  uvx --with modal modal run measure_alpha.py

Writes local/draft_v2/data/4_7_alpha_divergence/measured_alpha.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

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

image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .apt_install("git", "curl", "build-essential", "ca-certificates", "libnuma1")
    .pip_install("vllm", "huggingface_hub", "datasets")
    .env({
        "HF_HOME": "/root/.cache/huggingface",
        "CUDA_HOME": "/usr/local/cuda",
        "PATH": "/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "VLLM_USE_FLASHINFER_SAMPLER": "0",
    })
)

app = modal.App("neurips-spec-lab-alpha")

FRONTEND_WRAP = (
    "You are a frontend engineer. Produce a complete single-file HTML page "
    "(inline CSS, no external assets) for the following brief. Output only the "
    "HTML, starting with <!DOCTYPE html>.\n\nBrief: {brief}"
)


def build_local_items() -> list[dict]:
    """Original LosslessBench tasks, verbatim from hydrated task.json files."""
    LB = Path.home() / "Documents/lily-memory/Build/LosslessBench"

    def task_prompt(lid: str) -> str:
        t = json.loads((LB / f"lossless100/hydrated/tasks/{lid}/task.json").read_text())
        return t["prompt"]

    items = []
    for lid in ["L035", "L036", "L037", "L038", "L039"]:
        items.append({"domain": "agentic_coding", "id": lid,
                      "prompt": task_prompt(lid)})
    # L101 is not hydrated locally; fill to 5 with OpenDesign originals (pilot10).
    for lid in ["L098", "L099", "L100"]:
        items.append({"domain": "front_end_design", "id": lid,
                      "prompt": task_prompt(lid)})
    with open(LB / "data_frontend/pilot10.jsonl") as f:
        for line in list(f)[:2]:
            r = json.loads(line)
            items.append({"domain": "front_end_design", "id": f"od{r['id']}",
                          "prompt": FRONTEND_WRAP.format(brief=r["prompt"])})
    for lid in ["L088", "L089", "L090", "L091", "L092"]:
        items.append({"domain": "creative_writing", "id": lid,
                      "prompt": task_prompt(lid)})
    return items


@app.function(
    image=image,
    gpu="H100",
    timeout=45 * 60,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=_secrets,
)
def measure(local_items: list) -> dict:
    import time

    from datasets import load_dataset
    from vllm import LLM, SamplingParams

    # Paper benchmarks, loaded from the original HF datasets in-container.
    gsm8k = load_dataset("openai/gsm8k", "main", split="test")
    humaneval = load_dataset("openai/openai_humaneval", split="test")
    items = [
        {"domain": "gsm8k_paper", "id": f"gsm8k_{i}", "prompt": gsm8k[i]["question"]}
        for i in range(5)
    ] + [
        {"domain": "humaneval_paper", "id": humaneval[i]["task_id"],
         "prompt": "Complete the following Python function.\n\n" + humaneval[i]["prompt"]}
        for i in range(5)
    ] + list(local_items)

    llm = LLM(
        model="Qwen/Qwen3-8B",
        trust_remote_code=True,
        speculative_config={
            "method": "dflash",
            "model": "z-lab/Qwen3-8B-DFlash-b16",
            "num_speculative_tokens": 16,
            "max_model_len": 32768,
        },
        max_model_len=32768,
        max_num_seqs=128,
        gpu_memory_utilization=0.85,
        enforce_eager=False,
        disable_log_stats=False,
    )

    def spec_counters() -> dict:
        c = {}
        for m in llm.get_metrics():
            if "spec_decode" in m.name:
                v = getattr(m, "value", None)
                if v is None:
                    v = getattr(m, "sum", None)
                if isinstance(v, (int, float)):
                    c[m.name] = v
        return c

    # Match DFlash Table 1 setup: Qwen3 thinking mode DISABLED.
    ctk = {"enable_thinking": False}
    llm.chat([{"role": "user", "content": "Say hi."}], SamplingParams(max_tokens=16),
             chat_template_kwargs=ctk)
    print("[counters after warmup]", spec_counters(), flush=True)

    sp = SamplingParams(temperature=1.0, max_tokens=1024)
    results: dict = {}
    for it in items:
        domain = it["domain"]
        before = spec_counters()
        t0 = time.time()
        out = llm.chat([{"role": "user", "content": it["prompt"]}], sp,
                       chat_template_kwargs=ctk)[0]
        dt = time.time() - t0
        after = spec_counters()
        delta = {k: after[k] - before.get(k, 0) for k in after}
        accepted = next((v for k, v in delta.items() if "accepted" in k), None)
        drafted = next(
            (v for k, v in delta.items() if "draft_tokens" in k or "proposed" in k),
            None,
        )
        drafts = next(
            (v for k, v in delta.items() if "num_drafts" in k and "tokens" not in k),
            None,
        )
        rec = {
            "id": it["id"],
            "tokens": len(out.outputs[0].token_ids),
            "seconds": round(dt, 1),
            "accepted": accepted,
            "drafted": drafted,
            "drafts": drafts,
            "alpha": round(accepted / drafted, 4) if accepted and drafted else None,
            "tau": round(accepted / drafts + 1, 2) if accepted and drafts else None,
        }
        results.setdefault(domain, {"prompts": []})["prompts"].append(rec)
        print(f"[{domain}/{it['id']}] alpha={rec['alpha']} tau={rec['tau']} "
              f"({rec['tokens']} tok, {dt:.1f}s)", flush=True)

    for domain, r in results.items():
        acc = sum(p["accepted"] or 0 for p in r["prompts"])
        dr = sum(p["drafted"] or 0 for p in r["prompts"])
        dn = sum(p["drafts"] or 0 for p in r["prompts"])
        r["alpha"] = round(acc / dr, 4) if dr else None
        r["divergence_dlk"] = round(1 - acc / dr, 4) if dr else None
        r["tau"] = round(acc / dn + 1, 2) if dn else None
        print(f"[{domain}] DOMAIN alpha={r['alpha']} tau={r['tau']} "
              f"D_LK={r['divergence_dlk']}", flush=True)
    return results


@app.local_entrypoint()
def main():
    ROOT = Path(__file__).resolve().parents[3]
    out_dir = ROOT / "local/draft_v2/data/4_7_alpha_divergence"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = measure.remote(build_local_items())
    f = out_dir / "measured_alpha.json"
    f.write_text(json.dumps(results, indent=1))
    print("saved ->", f)
    for d, r in results.items():
        print(f"{d}: alpha={r['alpha']} tau={r['tau']} D_LK={r['divergence_dlk']}")
