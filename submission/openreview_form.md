# OpenReview Form

NeurIPS 2026 Education Track · https://openreview.net/group?id=NeurIPS.cc/2026/Education_Track
Deadline: **Sept 4, 2026**

---

## Title

Speculative Decoding: What's Measured, What's Missed, and What's Next

## Author

Lily Zhang, Madison Kanna

## TLDR

An interactive resource that teaches speculative decoding as the field evaluates it: three generations of draft models (EAGLE-3, DFlash, DSpark), why theory says measuring acceptance is enough, what that measurement misses (the standard harness never grades outputs; a vendor-assembled accelerated stack loses 5.6 behavior points where an owner-trained one loses 0.3), and a hands-on lab where learners turn the lossless knob themselves.

## The concept (≤200 words)

Speculative decoding accelerates LLM inference without changing the model's output, in theory. Autoregressive decoding is memory-bandwidth bound: generating one token streams the entire weight matrix from HBM while compute sits idle, so verifying K tokens costs about as much as generating one. A small draft model proposes K tokens; the target verifies them in a single pass via rejection sampling, preserving the output distribution exactly. Because correctness is guaranteed by construction, the field evaluates on efficiency alone, and its harnesses never grade a single answer.

Why now: acceleration is moving into the model itself (FP8 pre-training, MXFP4 quantization-aware training, INT4 benchmark reporting, Kimi K3's shipped speculator), every major serving provider ships a variant, and real usage (roleplay, marketing, agentic workflows) sits far from the math/code domains where verification concentrates. This resource teaches the whole arc: EAGLE-3 to DFlash to DSpark, what's measured, what's missed (a 0.3 vs 5.6-point behavior gap between owner-trained and vendor-assembled stacks), and what's next, the quality-aware draft training nobody has built. Learners finish by reproducing every number themselves on one GPU.

## Leveling and prerequisite knowledge

Introductory-to-intermediate. Accessible to any engineer or student who knows that an LLM generates text one token at a time. Prerequisites: basic familiarity with transformer inference (a forward pass produces a next-token distribution). No reinforcement learning, training, or GPU-kernel background required. The rejection-sampling losslessness argument is presented intuitively, with the accept/repair rule optional for readers who want the math.

## Learning objectives and outcomes

After engaging with this resource, a learner can:

- Explain WHY speculative decoding is possible (memory-bandwidth-bound decoding; verifying K tokens ≈ the cost of one), and read acceptance length correctly: accepted proposals per verification step, not saved passes.
- Trace the EAGLE-3 → DFlash → DSpark progression, name the bottleneck each stage removes, and explain why the training objective and the evaluation metric converged onto the same number.
- Demonstrate hands-on that acceptance rate is not accuracy: sweep the confidence threshold in the official evaluation code, grade the outputs, and watch the two numbers move in opposite directions.
- Articulate the domain mismatch (verification concentrates where acceptance is naturally highest, math and code, while usage concentrates elsewhere) and pose the open question: what would a draft-training objective that preserves long-tail behavior look like?

## Teaching material summary

All materials are original and created for this track. (1) An interactive self-contained HTML article walking the What's Measured / What's Missed / What's Next arc, built around the four-stage walkthrough figure and an interactive component with adjustable draft length. (2) A one-afternoon, one-GPU lab: reproduce the reported EAGLE-3 acceptance length (2.4–2.8) on Qwen3-8B, compare the three released DeepSpec checkpoints (EAGLE-3 vs DFlash vs DSpark) on one prompt set, sweep --confidence-threshold while grading outputs for correctness, and a pick-a-domain exercise rerunning the measurements outside math and code. (3) A short video walkthrough recorded against the interactive site. All figures are original; numbers cite the DSpark paper and the LosslessBench evaluation.

---

## File uploads

- **PDF** → `submission/2_page_pdf/submission.pdf` (2 pages)
- **Educational material ZIP**
