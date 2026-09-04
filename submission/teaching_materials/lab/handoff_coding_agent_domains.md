# Handoff: evaluate Coding and Agent Workflow (the two missing radar axes)

Goal: complete the five-domain radar. Two arms only, vanilla Qwen3-8B vs the same
model + DFlash draft (z-lab/Qwen3-8B-DFlash-b16). Metric is win count per task,
a tie scores one point for each side. Report absolute counts (X/N). Do not report
averages as the headline. Conventions: `Build/LosslessBench/JUDGING.md`.

## Step 0: the blocker, and the two ways through it

Both domains use agentic harnesses (tau3, Terminal-Bench) that must call an
OpenAI-compatible HTTP endpoint themselves. The DFlash lane currently only runs
on vLLM's offline `LLM()` path, which has no server. `vllm serve` crashes on
DFlash in stable 0.28.0 (engine-core init, CUDA device-side assert, and
`--enforce-eager` does not fix it, see `failures.md` R10).

Try in this order, stop at the first that passes the gate:

1. **vLLM serve + the two missing fields (untested hypothesis).** The passing
   offline config differs from our serve command in exactly two fields:
   `trust_remote_code=True` and `"max_model_len": 32768` inside
   speculative-config (plus top-level max-model-len 32768). Port both into
   `modal_vllm_serve.py`'s dflash branch and deploy once.
2. **SGLang serve (merged by the DFlash authors, CI-proven for Llama).**
   SGLang PR #35371 added DFLASH serving. Its CI test
   (`test/registered/spec/dflash/test_dflash.py`) launches a real server with:
   `--speculative-algorithm DFLASH --speculative-draft-model-path <draft>
   --trust-remote-code --mem-fraction-static 0.7` and gates on GSM8K accuracy
   >= 0.75 and acceptance length >= 2.8. CI uses Llama-3.1-8B + z-lab Llama
   draft. Qwen3-8B + z-lab/Qwen3-8B-DFlash-b16 is unverified but all parts
   exist. Our `modal_sglang_serve.py` already has a dflash mode: add
   `--trust-remote-code`, deploy with
   `SPEC_MODE=dflash DRAFT_MODEL=z-lab/Qwen3-8B-DFlash-b16`.

**Acceptance gate (mandatory before collecting any data):** server healthy, a
probe generation is faster than vanilla, and the acceptance counters show
tau >= 2 (vLLM: `/metrics` spec_decode counters, SGLang: server log accept
length). If tau is about 1, the config is broken in the R5 way. Stop and do not
collect data. Record the attempt in `failures.md`.

Vanilla arm serves as usual: `APP_NAME=neurips-spec-lab-vanilla SPEC_MODE=vanilla
modal deploy modal_vllm_serve.py`.

## Domain 1: Agent Workflow (tau3)

- Harness: `~/Documents/projects/tau2-bench`, branch **fix/ab-scoring-artifacts**
  (has `src/tau2/metrics/paired_ab.py` and API-key redaction; PR
  lilyzhng/tau2-bench#1). Do not run on the old branch, its scoring produced the
  T19 artifact (`Build/LosslessBench/INCIDENTS.md` INC-2026-09-03).
- Task set: pick 10 tasks from ONE domain (retail is well-trodden), write the
  task-id list down first, run the identical list on both arms.
- Arm wiring: agent = llm_agent pointed at the arm's endpoint (api_base = the
  Modal URL, any api_key string, model "default"). User simulator pinned
  `openai/gpt-4o` temperature 0 for BOTH arms. Temperature 0 on the agent too.
- Scoring: `python -m tau2.metrics.paired_ab <results_a> <results_b>`. Episodes
  that die of infrastructure are rerun or dropped from both arms. Per-task
  winner by reward on paired episodes, tie scores one point each.
- Ops: one harness process per server (failures.md R9). Expect ~30-60 min per
  arm for 10 tasks. Do not detach, watch it, save incrementally.

## Domain 2: Coding (Terminal-Bench)

- LosslessBench's coding axis is Terminal-Bench pass rate. Existing machinery:
  `Build/LosslessBench/tb2_tasks/`, `scripts/run_tb2_genheavy.sh`,
  `harbor_datasets/`. Memory gotchas: τ³/Harbor on Modal needs bwrap flags
  (see shared memory project_tau3_banking_eval).
- Task set: 10 tasks, same list both arms, ids written down before launch.
- The harness calls the arm endpoint the same way as tau3 (OpenAI-compatible).
- Scoring: pass/fail per task per arm. Winner = the arm that passes where the
  other fails, both pass or both fail = tie (one point each).
- If Terminal-Bench setup fights back for more than ~1 hour, fall back to a
  lighter proxy and label it clearly: HumanEval subset (10 problems, pass@1,
  same win-count rule). A labeled proxy beats an unlabeled blocker.

## Deliverables

1. `local/draft_v2/data/4_6_radar_pilot/agent_results/` and `coding_results/`
   with raw outputs plus a `win_counts.json` each:
   `{"vanilla": X, "dflash": Y, "n": N, "ties": T, "task_ids": [...]}`.
2. Update the radar to five axes using the handoff at
   `local/draft_v2/demo/radar_handoff_for_kimi.md` (original SVG:
   `~/Documents/Development/lilyzhng.github.io/writing/losslessbench/radar-v4.svg`).
   Axis values = win rate x100 for frontend, creative, agent, coding, and
   accuracy for guardrail (80 / 80).
3. One paragraph of findings per new domain in
   `local/draft_v2/data/4_6_radar_pilot/interactive_report.md` style: counts,
   the tasks that separated the arms, evidence for each.
4. `failures.md` entries for anything that broke.
5. `modal app list` shows zero running neurips apps at the end.

## Budget

One serve-fix test (~15 min GPU), then two arms x two domains of harness runs.
Rough total 3-5 H100 hours, ~$15-25. If the serve fix fails on both paths, stop
and report. Do not substitute DSpark, do not change the target model. The
five-domain radar waits until DFlash can serve.
