# LosslessBench (slim copy for the NeurIPS 2026 Education Track submission)

LosslessBench is our five-domain evaluation (coding, agent workflows, creative
writing, guardrails, frontend design) used in Section 2.3 of the interactive
website and in the hands-on lab.

This folder carries the source of the benchmark; the hydrated task data
(~208MB, above the per-resource size guidance) is hosted permanently on
Hugging Face:

- Dataset: https://huggingface.co/datasets/lilyzhng/lossless100
- Docker image: `alchemz/lossless100`

Contents:
- `lossless100_manifest.csv` / `lossless_balanced24_manifest.csv`: the task manifests.
- `fetchers/`: hydrator scripts that rebuild the full task data from public sources.
- `docker/`: container configuration to run the benchmark.
