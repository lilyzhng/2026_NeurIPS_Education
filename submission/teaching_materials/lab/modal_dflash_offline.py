#!/usr/bin/env python3
"""DFlash via vLLM's offline LLM path, copying the official acceptance test.

`vllm serve` crashes on DFlash in stable 0.28.0, but the upstream acceptance
test (tests/v1/e2e/spec_decode/acceptance_rates/dflash/test_dflash.py) runs the
offline LLM class with z-lab/Qwen3-8B-DFlash-b16 and passes CI. This script is
that config verbatim, generating the lab's two race prompts.

  uvx --with modal modal run modal_dflash_offline.py

Writes dflash outputs + meta into local/draft_v2/data/{4_4_frontend,4_5_creative}.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

FRONTEND_PROMPT = (
    "You are a frontend engineer. Produce a complete single-file HTML page "
    "(inline CSS, no external assets) for the following brief. Output only the "
    "HTML, starting with <!DOCTYPE html>.\n\n"
    "Brief: Stunning translucent calendar popup that smoothly blends into the "
    "interface."
)
CREATIVE_PROMPT = (
    "Historical Fiction: Write a scene from a story set during the height of "
    "the Roman Empire, focusing on a slice of a day in the life of a gladiator. "
    "Do not write a combat scene. Use sensory details to capture the sights, "
    "sounds, and smells of ancient Rome. Explore the gladiator's thoughts and "
    "emotions. The story should also touch on the larger political and social "
    "issues of the time period. The piece should feel like a slice of a larger "
    "story. First person, past tense, 1000 words."
)

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
    .pip_install("vllm", "huggingface_hub")
    .env({
        "HF_HOME": "/root/.cache/huggingface",
        "CUDA_HOME": "/usr/local/cuda",
        "PATH": "/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "VLLM_USE_FLASHINFER_SAMPLER": "0",
    })
)

app = modal.App("neurips-spec-lab-dflash-offline")


@app.function(
    image=image,
    gpu="H100",
    timeout=45 * 60,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=_secrets,
)
def generate() -> dict:
    import time

    from vllm import LLM, SamplingParams

    # Verbatim from the official QWEN3_DFLASH acceptance test.
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

    results = {}
    for label, prompt, max_tokens in [
        ("frontend", FRONTEND_PROMPT, 6000),
        ("creative", CREATIVE_PROMPT, 3000),
    ]:
        t0 = time.time()
        out = llm.chat(
            [{"role": "user", "content": prompt}],
            SamplingParams(temperature=0, max_tokens=max_tokens),
        )[0]
        dt = time.time() - t0
        tokens = len(out.outputs[0].token_ids)
        results[label] = {
            "text": out.outputs[0].text,
            "seconds": round(dt, 1),
            "completion_tokens": tokens,
            "tokens_per_s": round(tokens / dt, 1),
        }
        print(f"[{label}] {tokens} tok in {dt:.1f}s = {tokens/dt:.1f} tok/s", flush=True)

    try:
        for m in llm.get_metrics():
            if "spec_decode" in m.name:
                print(f"[metric] {m.name} = {getattr(m, 'value', getattr(m, 'sum', '?'))}",
                      flush=True)
    except Exception as e:  # metrics API varies by version; speed numbers stand alone
        print(f"[metric] unavailable: {e}", flush=True)
    return results


RACE_DOMAINS = {
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


@app.function(
    image=image,
    gpu="H100",
    timeout=45 * 60,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=_secrets,
)
def race() -> dict:
    """race_domains.py's bench (512 tok, greedy, median of 5) on the offline path."""
    import statistics
    import time

    from vllm import LLM, SamplingParams

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
    sp = SamplingParams(temperature=0, max_tokens=512)
    llm.chat([{"role": "user", "content": "Say hi."}], SamplingParams(max_tokens=16))  # warmup

    results = {}
    for domain, prompt in RACE_DOMAINS.items():
        speeds = []
        for _ in range(5):
            t0 = time.time()
            out = llm.chat([{"role": "user", "content": prompt}], sp)[0]
            dt = time.time() - t0
            speeds.append(len(out.outputs[0].token_ids) / dt)
        results[domain] = {"tokens_per_s_median": round(statistics.median(speeds), 1),
                           "runs": [round(s, 1) for s in speeds]}
        print(f"[{domain}] median {results[domain]['tokens_per_s_median']} tok/s "
              f"runs={results[domain]['runs']}", flush=True)

    try:
        for m in llm.get_metrics():
            if "spec_decode" in m.name and hasattr(m, "value"):
                print(f"[metric] {m.name} = {m.value}", flush=True)
    except Exception as e:
        print(f"[metric] unavailable: {e}", flush=True)
    return results


@app.function(
    image=image,
    gpu="H100",
    timeout=45 * 60,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=_secrets,
)
def pilot(items: list) -> dict:
    """Radar-pilot prompts on the DFlash lane (greedy, warmup burned)."""
    import time

    from vllm import LLM, SamplingParams

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
    llm.chat([{"role": "user", "content": "Say hi."}], SamplingParams(max_tokens=16))
    out = {}
    for it in items:
        t0 = time.time()
        r = llm.chat(it["messages"], SamplingParams(temperature=0, max_tokens=it["max_tokens"]))[0]
        dt = time.time() - t0
        tokens = len(r.outputs[0].token_ids)
        key = f"{it['domain']}_{it['id']}"
        out[key] = {"text": r.outputs[0].text, "seconds": round(dt, 1),
                    "completion_tokens": tokens,
                    "tokens_per_s": round(tokens / dt, 1),
                    **({"gold": it["gold"]} if "gold" in it else {})}
        print(f"[dflash] {key}: {tokens} tok in {dt:.1f}s", flush=True)
    return out


@app.local_entrypoint()
def pilot_main(hard: bool = False):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pilot_radar_prompts import build, build_hard

    ROOT = Path(__file__).resolve().parents[3]
    out_dir = ROOT / "local/draft_v2/data/4_6_radar_pilot/dflash"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = pilot.remote(build_hard() if hard else build())
    metaf = out_dir / "meta.json"
    meta = json.loads(metaf.read_text()) if metaf.exists() else {}
    for key, r in results.items():
        (out_dir / f"{key}.txt").write_text(r.pop("text"))
        meta[key] = r
    metaf.write_text(json.dumps(meta, indent=1))
    print("saved", len(meta), "items ->", out_dir)


@app.local_entrypoint()
def race_main():
    ROOT = Path(__file__).resolve().parents[3]
    results = race.remote()
    f = ROOT / "local/draft_v2/data/4_2_race_vllm.json"
    data = json.loads(f.read_text()) if f.exists() else {}
    data["dflash_zlab_offline"] = results
    f.write_text(json.dumps(data, indent=1))
    print("saved dflash_zlab_offline ->", f)


@app.local_entrypoint()
def main():
    ROOT = Path(__file__).resolve().parents[3]
    results = generate.remote()
    for label, subdir, suffix in [("frontend", "4_4_frontend", ".html"),
                                  ("creative", "4_5_creative", ".md")]:
        out_dir = ROOT / f"local/draft_v2/data/{subdir}"
        out_dir.mkdir(parents=True, exist_ok=True)
        r = results[label]
        (out_dir / f"dflash{suffix}").write_text(r.pop("text"))
        metaf = out_dir / "meta.json"
        data = json.loads(metaf.read_text()) if metaf.exists() else {}
        data["dflash"] = {"label": "dflash", **r}
        metaf.write_text(json.dumps(data, indent=1))
        print(f"[{label}] {r}")
