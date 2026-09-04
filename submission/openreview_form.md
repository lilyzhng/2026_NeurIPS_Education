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

An interactive website and hands-on lab teaching speculative decoding: why it is fast, why it is lossless in theory, three generations of draft models (EAGLE-3, DFlash, DSpark), and cross-domain evaluation with LosslessBench.

## The concept

- **Why it matters:** every LLM generates one token at a time. Autoregressive decoding is a major bottleneck of inference: producing n tokens takes n passes through a model with tens of billions of parameters. Speculative decoding accelerates this, and it now runs under nearly every hosted LLM: OpenAI credited its 80% GPT-5.6 Luna price cut partly to a redesigned draft model, Anthropic's fast mode serves the same Claude Opus model up to 2.5x faster, DeepSeek ships DSpark for a 51% throughput gain, and Kimi K3 ships with its own draft model.
- **How it works:** a lightweight draft model proposes the next tokens, the target model verifies all of them in a single forward pass at nearly the cost of one, and rejection sampling guarantees the output follows the target distribution.
- **Three generations, each removing one bottleneck:** EAGLE-3 raises acceptance length, DFlash cuts drafting time, DSpark cuts verification time, and DFlash 2 pushes acceptance length further.
- **Beyond coding and math:** to answer whether these methods generalize across domains beyond coding and math, which account for only 17% of real traffic, we built LosslessBench, a five-domain evaluation, and a hands-on lab where learners measure the trade-offs themselves.

## Leveling and prerequisite knowledge

Introductory-to-intermediate; accessible to any engineer or student who knows that an LLM generates text one token at a time. Prerequisites: basic familiarity with transformer inference. The rejection-sampling losslessness argument is presented intuitively; hands-on labs are optional for participants who want more depth.

## Learning objectives and outcomes

After engaging with this resource, a learner can:

- Understand why autoregressive decoding is the major bottleneck of LLM inference.
- Recognize how widely speculative decoding runs in production today (OpenAI, Anthropic, DeepSeek, Kimi), and why decoding speed and quality affect everyone.
- Explain why speculative decoding is fast, and why it is lossless in theory.
- Trace the evolution of draft models from the 2023 origin through EAGLE-3, DFlash, DSpark, and DFlash 2, and name the bottleneck each generation removes.
- Evaluate a speculative decoding model across domains with LosslessBench.
- Serve and evaluate speculative decoding models hands-on, including adjusting the acceptance threshold the way a deployment would.

## Grounding in NeurIPS Research (2022–2026)

The resource covers recent papers at NeurIPS and its sister venues:

- Speculative decoding (ICML 2023): the foundational draft-and-verify algorithm and its losslessness proof, the subject of Section 1. https://arxiv.org/abs/2211.17192
- EAGLE-3 (NeurIPS 2025): feature-level drafting with multi-layer fusion and a training-time test, the current autoregressive-draft baseline, Section 1.1. https://arxiv.org/abs/2503.01840
- DFlash (ICML 2026): a block-diffusion drafter that generates the whole block in one forward pass, over 6x lossless acceleration and up to 2.5x over EAGLE-3, Section 1.2. https://arxiv.org/abs/2602.06036
- DSpark (DeepSeek, 2026): confidence-scheduled verification on the block-parallel backbone, serving DeepSeek-V4-Flash 60–85% faster in production, Section 1.3. https://arxiv.org/abs/2607.05147
- ViSpec (NeurIPS 2025): vision-aware speculative decoding, grounding the multimodal direction, Section 3.1. https://neurips.cc/virtual/2025/poster/115277

The venue lineage: blockwise parallel decoding (NeurIPS 2018), lossless speculative decoding (ICML 2023), EAGLE-3 (NeurIPS 2025), DFlash (ICML 2026); on the training side, FP8 in DeepSeek-V3, MXFP4 QAT in gpt-oss, and Kimi K3 shipping the speculator in post-training.

## Teaching material summary

All materials, including LosslessBench, are original and created for this track:

- **Interactive self-contained website** following the What Lossless Means / What It Doesn't / What's Next arc, with an interactive walkthrough and an acceptance-rate demo.
- **Hands-on lab** with a Jupyter notebook walkthrough, every measured result embedded: serve Qwen3-8B with the three released draft checkpoints (EAGLE-3 vs DFlash vs DSpark), reproduce published acceptance lengths, race the lanes across domains, and measure per-domain performance on LosslessBench.
- All materials, including the interactive article and lab code, are publicly available through the interactive website.

---

## File uploads

- **PDF** → `submission/2_page_pdf/submission.pdf` (2 pages)
- **Educational material ZIP**
