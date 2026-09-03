# Section 4 Hands-on Lab — code

Scripts behind the article's Section 4 ("How to Train, Serve, and Test It"). One H100 (or A100-80GB), one afternoon. Design log: `local/draft_v2/04_how_to_train_serve_test.md` + wavemind artifact `20260902-neurips-section4-handson-design.md`.

## Files

- `modal_sglang_serve.py` — SGLang server on Modal. `SPEC_MODE=vanilla` (baseline) or `SPEC_MODE=eagle3` (DeepSpec EAGLE-3 speculator `deepseek-ai/eagle3_qwen3_8b_ttt7` on target `Qwen/Qwen3-8B`).
- `bench_41.py` — stdlib bench: waits for `/health`, 1 warmup + N timed generations of the Figure-1 passage prompt, tokens/s per run, scrapes `/metrics` for `spec_accept_length` (τ), incremental-saves to `local/draft_v2/data/4_1_bench.json`.

## 4.1 steps (as run for the article's numbers)

```bash
# 0. launch FIRST, read the article while it warms (cold start ≈ 10 min once:
#    image build ~6 min + 16GB weight download into the HF cache volume ~4 min;
#    both are cached afterwards)
SPEC_MODE=vanilla uvx --with modal modal deploy modal_sglang_serve.py

# 1. baseline numbers
python3 bench_41.py --url https://<you>--neurips-lab-sglang-serve.modal.run --label vanilla

# 2. redeploy with the speculator (image + weights now cached: fast)
SPEC_MODE=eagle3 uvx --with modal modal deploy modal_sglang_serve.py
python3 bench_41.py --url https://<you>--neurips-lab-sglang-serve.modal.run --label eagle3

# 3. STOP the app — the server holds the GPU until you do
uvx --with modal modal app stop neurips-lab-sglang
```

## Cold-start playbook (for workshop / readers)

- **Launch first, learn while it warms.** The lab's step 0 is the deploy command; the ~10 min cold start overlaps with reading. In a live workshop: everyone runs step 0 at the session open, hands-on happens at the end.
- **Shared warm endpoint** (workshop day): we pre-deploy one endpoint so people can `curl` immediately while their own deploy warms.
- Phase 2: publish a pre-built Docker image to cut image build to a registry pull.

## SGLang flags used (from [SGLang speculative decoding docs](https://docs.sglang.io/advanced_features/speculative_decoding.html))

```
--speculative-algorithm EAGLE3
--speculative-draft-model-path deepseek-ai/eagle3_qwen3_8b_ttt7
--speculative-num-steps 3 --speculative-eagle-topk 4 --speculative-num-draft-tokens 16
```

DFlash: `--speculative-algorithm DFLASH` is supported by SGLang (used in 4.2). DSpark serving support: not in SGLang docs as of 2026-09; 4.2 will document what works.

## Notes

- GPU numbers scale with hardware. The article's Section 1 walkthrough is B200; these runs are H100. **The ratios are what should match, not the absolute tokens/s.**
- Modal free tier ($30/month credits) covers the afternoon; a full 4.1 run is a few dollars.
