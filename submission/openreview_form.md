# OpenReview Form

NeurIPS 2026 Education Track · https://openreview.net/group?id=NeurIPS.cc/2026/Education_Track
Deadline: **Sept 4, 2026**

Interactive website: https://neurips2026-speculative-decoding.vercel.app/

---

## Title

Speculative Decoding: What Lossless Means, What It Doesn't, and What's Next

## Author

Lily Zhang, Madison Kanna

## TLDR

An interactive resource that teaches speculative decoding the way the field evaluates it: three generations of draft models (EAGLE-3, DFlash, DSpark), why the result is lossless in theory, what the standard harness never measures (token quality outside math and code; a 5.6-point behavior gap between owner-trained and vendor-assembled stacks), and a one-GPU lab where learners serve an accelerated model and grade the outputs themselves.

## The concept (≤200 words)

The market wants more tokens: agent workflows chain dozens of model calls per task, reasoning models spend thousands of tokens thinking, and every product built on either one pays for latency twice, in compute and in user patience. The ideal answer is lossless inference acceleration, and that demand has pulled acceleration steadily deeper into the model itself: draft models evolved through three generations in two years — EAGLE-3 (~3.9 tokens/pass), DFlash (~4.4), DSpark (~5.1) — alongside FP8 pre-training, MXFP4 quantization-aware training, and Kimi K3's shipped speculator. A small draft proposes K tokens; the target verifies all K in a single forward pass at nearly the cost of one, and rejection-sampling verification guarantees the output distribution exactly. Because correctness is guaranteed by construction, evaluation collapsed onto acceptance length and tokens/s — the standard harness never grades a single answer — while the behavior gap between owner-trained and vendor-assembled stacks reaches 5.6 points on long-tail domains. Learners walk all three generations, then reproduce every number themselves on one GPU.

## Leveling and prerequisite knowledge

Introductory-to-intermediate. Accessible to any engineer or student who knows that an LLM generates text one token at a time. Prerequisites: basic familiarity with transformer inference (a forward pass produces a next-token distribution). No RL, training, or GPU-kernel background required. The rejection-sampling losslessness argument is presented intuitively, with the accept/repair rule optional for readers who want the math.

## Learning objectives and outcomes

After engaging with this resource, a learner can:

- Explain why speculative decoding is possible (verifying K tokens ≈ the cost of one), and read acceptance length correctly: accepted proposals per verification step, not saved passes.
- Walk through EAGLE-3, DFlash, and DSpark, name the bottleneck each stage removes, and explain why the training objective and the evaluation metric converged onto the same number.
- Demonstrate hands-on that acceptance rate is not accuracy: sweep the confidence threshold in the official evaluation code, grade the outputs, and watch the two numbers move in opposite directions.
- Articulate the domain mismatch (verification concentrates in math and code, usage concentrates elsewhere) and pose the open question: what would a draft-training objective that preserves long-tail behavior look like?

## Grounding in NeurIPS Research (2022–2026)

The three generations the resource teaches are themselves recent papers at NeurIPS and its sister venues:

- EAGLE-3 (NeurIPS 2025): feature-level drafting with multi-layer fusion and a training-time test, the current autoregressive-draft baseline.
- DFlash (ICML 2026): a block-diffusion drafter that generates the whole block in one forward pass, over 6× lossless acceleration and up to 2.5× over EAGLE-3.
- DSpark (DeepSeek, 2026): confidence-scheduled verification on the block-parallel backbone, serving DeepSeek-V4-Flash 60–85% faster in production.

The walkthrough places them in the NeurIPS speculative-decoding line they extend — SpecTr (NeurIPS 2023), Sequoia (NeurIPS 2024), and SpecExec (NeurIPS 2024) — alongside the foundational papers (Leviathan et al., 2023; Chen et al., 2023), FP8 pre-training in DeepSeek-V3 (2024), MXFP4 QAT in gpt-oss (2025), Judge Decoding (ICLR 2025), and Kimi K3 shipping the speculator as part of post-training (2026).

## Teaching material summary

All materials are original and created for this track. (1) An interactive self-contained HTML article following the What Lossless Means / What It Doesn't / What's Next arc, with a walkthrough with adjustable draft length. (2) A hands-on lab on a single GPU: serve Qwen3-8B with the three released draft checkpoints (EAGLE-3 vs DFlash vs DSpark), reproduce published acceptance lengths, race the lanes on frontend and creative briefs, and measure per-domain acceptance across the five LosslessBench domains. All materials, including the interactive article and lab scripts, are publicly available through the interactive website.

---

## File uploads

- **PDF** → `submission/2_page_pdf/submission.pdf` (2 pages)
- **Educational material ZIP**
