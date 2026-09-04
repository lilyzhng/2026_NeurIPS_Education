# Andrew's Feedback — 2026-09-03 (Slack + call)

All feedback from Andrew Hartnett on the NeurIPS Education submission, one item per row, with status. Verbatim quotes preserved. Sources: [call debrief](20260903_andrew-conversation-debrief.md) · [raw Slack + transcript](20260903_andrew-conversation-debrief-sources.md).

## Writing & structure

| # | Feedback | His words | Status |
|---|---|---|---|
| 1 | Keep title candidate 1, anchor on Speculative Decoding | hit the reader with the anchor/term that they will recognize | ✅ Kept anchor; third beat later changed to What's Next per review |
| 2 | Back up the intro, don't lose the audience. 5 beats: bottleneck → 2023 → draft+verify in plain words → lossless hook → speedup | As it is now .. you are too deep, too fast. You will lose anyone that doesn't know what 'draft' is | ✅ Intro rewritten (Every-LLM lead-in, 3 paragraphs) |
| 3 | De-jargon What lossless means first paragraph (B200, SGLang, vanilla) | at the very least you might want to have a hover over glossery? | ⬜ Not done |
| 4 | Is Figure 1 going to be animated? | | ⬜ Open question |
| 5 | Table 1: introduce acceptance length (τ) before per-token latency; use non-integer τ in examples | I'd be in favor of using a non-integer /tau as that seems unlikely | ⬜ Not done |
| 6 | Cut section 3.3, end with a holistic conclusion | the last thing the reader reads is the most tangential | ⬜ Pending (Lily asked if spec-tool section should go too; no reply yet) |

## The lossless argument (the call)

| # | Feedback | His words | Status |
|---|---|---|---|
| 7 | Define lossless as a statistical distribution concept first, then pivot to utility | that's really a statement about the sampling probabilities for every token in the vocabulary | ✅ Definition + theorem chain in Section 1 |
| 8 | LosslessBench doesn't feel like it measures loss; measure distributional divergence | I would expect a measure of that property to be like the KL divergence (or similar) | ✅ Answered with the lineage's own metric: α = 1 − E[D_LK] (Thm 3.5), Figure 10 acceptance measurement across 7 groups |
| 9 | DFlash paper has no evidence of losslessness | they say the word, but I don't see any quantitative substance | ✅ Verified (no proof, no verification rule, no quality numbers); stated in article |
| 10 | Story arc: free lunch (2023) → relaxed preconditions → lossy, defended by narrow benchmarks | they broke the preconditions that made this a free lunch | ✅ Woven into Sections 1–2 |
| 11 | Figure 11 control: does vanilla ever produce the broken flash in 10 runs? | is the flash just one outcome from the vanilla model's own distribution? | ✅ Resolved differently: runs are temperature=0, deterministic; noted in analysis |
| 12 | NHTSA 1992 crash-test analogy for benchmark overfitting | | ⬜ Optional, not used |
| 13 | Best-pet analogy: pass rates test the mode, not the distribution | I'm not measuring whether it thinks the best pet is a cat | ✅ Figure 7 pet-distribution figure covers this |
| 14 | Why is the draft lossy? Two hypotheses: distillation below generalization threshold, or broken algorithm mechanics | | ⬜ Future-work material |

## Section 3

| # | Feedback | His words | Status |
|---|---|---|---|
| 15 | Multimodal section works; token-density question | vision tokens carry a lot more information than text tokens ... there just might not be as much juice to squeeze | ⬜ Consider adding a line |
| 16 | Tool-call section: connect back to CPU speculative execution / branch prediction | which is really the origin of speculative decoding being called 'speculative' | ⬜ Not done |

## Track fit

| # | Feedback | His words | Status |
|---|---|---|---|
| 17 | Track blurb unclear; ask organizers, look at what gets accepted | I don't think they know ... they're gonna kinda figure it out on the fly | ✅ Email sent to education-chairs 09-04 |

**Remaining before submission (quick wins): #3 de-jargon, #5 Table 1 order + non-integer τ, #6 cut 3.3 + conclusion.**
