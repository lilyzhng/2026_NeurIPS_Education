# Section 4 Hands-on Lab — code

Scripts behind the article's Section 4 ("Hands-On Lab"). One H100 (or A100-80GB), one afternoon, all draft weights from the [DeepSpec](https://github.com/deepseek-ai/DeepSpec) release (one training recipe across algorithms, so cross-algorithm comparisons stay controlled).

## Engine map (verified 2026-09-02, the hard-won part)

| DeepSpec checkpoint | SGLang | vLLM |
|---|---|---|
| `dspark_qwen3_8b_block7` | ✅ | ✅ |
| `eagle3_qwen3_8b_ttt7` | ❌ no Qwen3-shaped EAGLE3 draft class | ✅ `qwen3_eagle3` |
| `dflash_qwen3_8b_block7` | ❌ rejected (`markov_rank=0`) | ✅ with a one-line arch relabel (done in the serve script) |

So: **4.1 / 4.2 / 4.4 run on vLLM** (`modal_vllm_serve.py`, app `neurips-spec-lab`), **4.3 runs on SGLang** (`modal_sglang_serve.py`) because only SGLang exposes the acceptance-threshold knob (`--speculative-accept-threshold-*`); vLLM has none. That asymmetry is itself Section 2.2's lesson.

## Files

- `modal_vllm_serve.py` — vLLM server on Modal. `SPEC_MODE=vanilla|eagle3|dflash|dspark`.
- `modal_sglang_serve.py` — SGLang server (dspark lane + 4.3 threshold knob via `ACCEPT_THRESHOLD`).
- `measure_decoding_speed.py` — send a prompt, report tokens/s (+ τ from /metrics when exposed).
- `race_domains.py` — same measurement across coding / creative / frontend prompt sets.
- `sweep_threshold.py` — 4.3: redeploy per threshold, GSM8K subset at temperature 1.0 (thresholds only bite when sampling), accuracy + speed + τ per step.
- `generate_frontend_task.py` — 4.4: OpenDesign id 673 (the Figure 11 calendar brief), greedy; lossless ⇒ byte-identical HTML across lanes.
- `plot_lab.py` — figures from the collected JSONs in `local/draft_v2/data/`.

## Run

```bash
pip install modal && modal setup
SPEC_MODE=vanilla modal deploy modal_vllm_serve.py     # cold start ~10 min once, then cached
python3 measure_decoding_speed.py --url https://<you>--neurips-spec-lab-serve.modal.run --label vanilla
SPEC_MODE=dspark modal deploy modal_vllm_serve.py      # swap the speculator, rerun
# ... race_domains.py per lane, sweep_threshold.py for 4.3, generate_frontend_task.py for 4.4
modal app stop neurips-spec-lab                        # the server holds the GPU until stopped
```

Get $30 free credits by signing up for a [Modal](https://modal.com) account; an H100 is ~$4/hour and the full lab uses $8-12.

## Cold-start playbook

**Launch first, read while it warms.** Step 0 is the deploy command; the ~10 min cold start overlaps with reading. Workshop mode: everyone deploys at the session open, hands-on runs at the end. We also keep one pre-warmed shared endpoint on workshop day.

## Extension

Want DFlash2 (Section 1.4) or an SGLang-native EAGLE3 for this target? No public checkpoint exists — train your own with [SpecForge](https://github.com/sgl-project/SpecForge) (`configs/qwen3-8b-eagle3.json` ships in the repo; its EAGLE3 export is SGLang-servable by construction).
