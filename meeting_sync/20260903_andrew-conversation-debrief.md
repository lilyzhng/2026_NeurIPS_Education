# Conversation Debrief with Andrew — 2026-09-03

> Topic: LosslessBench framing, "lossless" claims, and NeurIPS Education tutorial scope
> Related: [submission/openreview_form.md](../submission/openreview_form.md) · [meeting_sync/20260815_kickoff.md](20260815_kickoff.md) · [Sources (Granola notes + raw transcript)](20260903_andrew-conversation-debrief-sources.md) · [Granola](https://notes.granola.ai/t/12e1ecc3-af34-4b07-acdf-7f4d7032adf2)
> Company: NeurIPS 2026 Education · Position: n/a · Stage: informational_call · Interviewer: Andrew · Mock: no
> Type: conversation

## Debrief

### Granola audit (notes vs transcript)

The notes are unusually good but missed five things the transcript has:
- Andrew's figure 11 control question: run **vanilla 10 times** — is the broken flash real degradation or one sample from vanilla's own distribution?
- The **best-pet analogy**: pass-rate evals test the mode ("best pet is a dog"), not the distribution ("does it ever say cat").
- The practical reader takeaway: if your task is outside coding/math and you control provider knobs, **back off aggressive speculative decoding**.
- DeepSeek's **verification scheduling peeking into the future** as a concrete example of algorithm-level breakage.
- Andrew's read that the Education track organizers **don't know what they want** ("they're figuring it out on the fly"; maybe they want a Chris Olah-style focused piece).
- ⚠️ Conflict: notes say dataset = "Open-Platypus"; transcript audio says something like "open perfect plan". Unverified — confirm the actual DeepSpec dataset name before citing.

### Summary

Andrew stress-tested the LosslessBench framing 24 hours before submission and handed Lily the story arc the article should carry: speculative decoding started as a theoretically lossless free lunch, companies relaxed the preconditions chasing 6x speedups, and they now verify only on a narrow benchmark set (GSM8K/math/coding) while 83% of real task domains go unmeasured. His core objection: "lossless" is a statement about sampling probabilities over the whole vocabulary, so the article must define it that way and then argue the pivot to utility-based evaluation explicitly. His concrete asks: run a token-level distributional comparison (logits over the vocab, a divergence measure), and check whether vanilla ever produces a broken output in 10 runs of the figure 11 task. On tutorial fit, neither of them knows what the new Education track wants; Lily will email the organizers and trim focus.

### ⭐ Top Suggestions

1. **Define "lossless" as identical sampling probabilities over the whole vocabulary, then argue the pivot to utility.** "That's really a statement about the sampling probabilities for every token in the vocabulary being identical to the core distribution."
   - **State the statistical definition first** — readers expect KL/log-prob measurement when they see "lossless"; the article currently skips this.
   - **Then make the pivot explicit** — practitioners care about the Pareto frontier of speed vs quality and perceptual evaluation, not the statistical guarantee.
   - **Adopt his story arc**: free lunch (original two papers) → preconditions relaxed for bigger speedups → now lossy, with companies assuming the original theoretical justification de facto holds without empirical verification.
2. **Add the token-level distributional measurement.** "You need to extract the logit for the whole vocabulary over a wide range of tasks and compute some sort of Bregman divergence — some distributional measure that says they're not the same."
   - He doesn't believe DFlash is lossless and found **no quantitative evidence in the DFlash paper** — they say the word, conditioned only on the rejection-sampling equation.
   - The equation's guarantee only holds under exact rejection sampling and residual-mass computation; the relaxations (figure 7 right panel) break it.
   - Lily committed on the call to running the draft-vs-target computation.
3. **Answer the figure 11 sampling-vs-degradation question.** "If you asked the vanilla model to do this task 10 times, does it ever produce something like the flash?"
   - One broken DFlash output could be a sample from vanilla's own distribution; run vanilla N times to show the failure is systematic bias, not variance.
   - Cheap to run, and it directly defends the benchmark's headline demo.
4. **Frame the overfitting claim with the NHTSA analogy and separate the two effects.**
   - NHTSA ~1992: when required crash tests changed, almost every previously-A-rated car failed — overfit to a constructed test set. Same claim: spec-decoding hill-climbing overfits a limited benchmark suite.
   - Base models already overfit coding/math via RL post-training; the article must show spec decoding **makes it worse**. His two candidate mechanisms: vanilla distillation from an overtrained base drops below the generalization threshold and widens the gap, or the algorithm itself is broken (DeepSeek verification scheduling peeking into the future).
   - Reader takeaway: outside coding/math, back off aggressive speculative decoding — you're paying for it even though providers don't advertise it.
5. **Email the Education track organizers about scope before trimming.**
   - Andrew found the track blurb incoherent ("reparametrization trick but not variational inference… I didn't quite follow") and thinks the organizers are figuring the new track out on the fly.
   - The tutorial "does a lot of things" (lit review + practice + hands-on + future work); unclear if they want breadth or a Chris Olah-style focused interactive piece.
   - Lily's call: email to confirm, then trim focus.

### Scorecard

**Overall: 7.5/10** — she extracted every high-value item Andrew had (definition fix, measurement plan, story arc, analogy) and left with owned actions, but spent the first third defending the current framing before absorbing, and one ask (multimodal section) burned a turn on material he hadn't read.

| Goal she brought in | Score /10 | Evidence |
|---|---|---|
| 1. Stress-test the "lossless" framing and get a concrete fix | 8 | Pushed back twice, then asked the exact right question — "you don't believe it's lossless, how do you want to convey that to the audience?" — which extracted the logits-over-vocab + Bregman divergence plan; committed to it on the call |
| 2. Get the article's narrative arc and strongest arguments | 8 | Mostly received rather than pulled, but confirmed alignment at each beat and synthesized it back as the two-level lossy structure (algorithm-level + overfitting-level), which Andrew then sharpened |
| 3. Resolve tutorial scope/depth and track fit (incl. multimodal) | 6 | Multimodal ask wasted (he hadn't read it); "is this too deep" got "I don't know what they're looking for" — but she converted that into a real action (email organizers, trim focus) |

**Goal average: 22 ÷ 3 = 7.3/10**

### Strengths

- Asked the extraction question of the night — "How do you want to convey that to the audience?" — flipping his skepticism from objection into a concrete measurement plan.
- Synthesized his points into her own structure live (the numbered two-level lossy argument), which he built on rather than repeated.
- Held her ground where she had real knowledge: explained the draft-model training recipe (SFT-style distillation, DeepSpec, open weights + dataset) when he admitted he lacked intuition for it.
- Ended with owned actions, not vague agreement: token-level computation, organizer email, trim focus.

### Weaknesses

- Defended the current framing for several turns before absorbing that Andrew was agreeing with her thesis and upgrading it.
- Asked about the multimodal paragraph without first checking whether he'd read it — a wasted ask in a time-boxed call.
- "I have confidence this will be accepted" — closed on an unearned-confidence note right after he said nobody knows what the track wants; harmless with a friend, but it's the assert-over-verify pattern.

### Revised scripts

#### Goal 3 — Tutorial scope / track fit（目标：get actionable scope guidance, not "I don't know"）

> - **Check first:** "Before I ask about specific sections — how far did you get? I'll only ask about parts you've read."
> - **Frame the trade-off, not the anxiety:** "The tutorial currently does four things: lit review, what companies actually ship, the hands-on lab, and future work. If you had to cut one to make it tighter, which goes first?"
> - **Use his read of the track:** "You read the track blurb — does it read like they want breadth, or a Chris Olah-style focused interactive piece?"
> - **Close with the action:** "I'll email the organizers to confirm and trim toward whichever they say. If they don't know either, I'll optimize for the focused version since that's more defensible in review."

### Flip the Table

1. **"How do you want to convey that to the audience?"**
   - Context: after Andrew said flatly he doesn't believe DFlash is lossless.
   - Question: "Okay. So you don't believe it's lossless. How do you want to convey that to the audience?"
   - Analysis: converted his skepticism into the concrete deliverable — extract logits over the whole vocabulary, compute a distributional divergence.
   - Why it worked: instead of defending, she made him design the fix. Best move of the call.
2. **"Do you think this tutorial is getting too deep?"**
   - Context: near the end, worried the hard questions exceed what she can answer.
   - Question: "Do you think this tutorial is getting too deep? Lots of the questions you brought up are beyond my reach."
   - Analysis: honest, but framed as anxiety rather than a scoping decision; got "I don't know what they're looking for."
   - Better version: "Which of the four things this tutorial does would you cut first to make it tighter?"

### Missed Opportunities

1. **The "why" hypotheses as future-work section**
   - Context: Andrew laid out two candidate mechanisms (distillation below generalization threshold; broken verification scheduling) and asked "why?" — she answered "answering why is very hard" and moved on.
   - Ask: "If I can't prove the why, can I frame your two hypotheses as the future-work section — distillation amplification vs algorithmic bias — and design one small experiment that distinguishes them?"
   - Impact: would have turned the hardest open question into a labeled Hypothesis section, exactly the forward-looking content he praised.
2. **The 10-run vanilla baseline scope**
   - Context: he asked whether vanilla ever produces a broken flash in 10 runs; she pivoted to benchmark design instead of scoping the experiment.
   - Ask: "That's cheap to run — 10 vanilla replays of figure 11's task. If vanilla never breaks and DFlash breaks reliably, is that the evidence bar you'd accept?"
   - Impact: locks his acceptance criterion before she spends the compute.

### Action items

- [ ] Token-level distributional comparison: draft vs target logits over the vocab, wide task range, divergence measure (Andrew's #1 ask; committed on call).
- [ ] Run vanilla ~10x on the figure 11 task; show breakage is systematic, not sampling variance.
- [ ] Rewrite the lossless definition paragraph: statistical definition first, then the utility pivot; adopt the free-lunch → relaxed → overfit story arc.
- [ ] Consider the NHTSA 1992 crash-test analogy for the overfitting section.
- [x] Verified (see Post-call research): DFlash paper asserts losslessness by inheritance, contains no proof, no stated verification rule, no distributional evidence — safe to write as observation with citation.
- [ ] Verify the DeepSpec training dataset name (Granola says Open-Platypus; DFlash itself uses UltraChat + ShareGPT) and review its data distribution.
- [ ] Email NeurIPS Education organizers about desired scope; trim tutorial focus accordingly.
- [ ] Andrew still owes feedback on the multimodal paragraph (he was reading it before bed).

### Post-call research (2026-09-03, answering the open questions from the call)

Verified against the [DFlash paper](https://arxiv.org/abs/2602.06036) (arXiv 2602.06036, full text pulled).

**Q1 — Does the DFlash paper contain any proof of losslessness? (Andrew's claim)**
- Confirmed: **no**. "Lossless" appears only as assertion — abstract ("over 6× lossless acceleration"), intro ("verification to ensure the final output remains lossless"), conclusion ("speculative verification provides a principled guarantee of output quality"). All inherited by citation from the speculative decoding paradigm (Leviathan et al. 2023).
- No theorem, no acceptance-rule math, no distributional measurement. The only equation is the latency/speedup formula (Eq. 1). Evidence provided = speedup, acceptance length τ, and benchmark tables (GSM8K / Math500 / AIME25 / HumanEval / MBPP / LiveCodeBench / MT-Bench).
- Sharper gap for the article: the paper **never states its verification rule** (exact rejection sampling or not) — only "verified in parallel by the target model". Losslessness would only be inherited under exact rejection sampling; that precondition is unstated and unverified.

**Q2 — How is the draft model actually trained? SFT or RL?**
- **SFT-style distillation, no RL.** Frozen target model serves as feature extractor; draft is a small block diffusion model.
- **KV injection**: full prompt+response passes through the frozen target; hidden states from layers sampled shallow-to-deep are concatenated, fused by a light projection, then injected as **Key/Value projections into every draft layer** (stored in draft KV cache, reused across iterations).
- **Objective**: random anchor tokens from the response start each block; remaining block_size−1 positions masked; draft predicts them in parallel. Loss = **cross-entropy with exponentially decaying position weights** w_k = exp(−(k−1)/γ) (Eq. 4) — early positions matter more because an early error invalidates the rest of the block.
- Shares token embedding + LM head with the target. Data: **UltraChat + ShareGPT** (same as EAGLE-3, §5.5.1). ⚠️ So Granola's "Open-Platypus" is wrong for DFlash (may belong to DeepSpec — still verify separately).

**Q3 — Why inject target hidden features into K/V specifically?**
- Without target conditioning, a 5-layer diffusion drafter only gets 2–3× speedup (Table 10) — hidden states carry more than logits (long-range deps, task semantics, implicitly future-token info, citing Samragh et al. 2025).
- EAGLE-3-style **input fusion** feeds target features only at the input layer → diluted as draft depth grows, acceptance gains plateau. **KV injection** exposes every draft layer's attention to the target features, so acceptance length scales with draft depth (§5.5.2). Ablation Table 9: KV beats input fusion on all tasks (e.g. GSM8K τ 4.8 vs 4.2 AR-drafting; 4.2 vs 3.5 block-diffusion).
- K/V (not Q) because the target features play the role of retrievable context memory that masked-position queries attend to.

**Q4 — Does Table 1 of DFlash check accuracy before measuring speedup?**
- No. The paper reports **zero task accuracy anywhere** — Table 1 (and all experiment tables) contain only speedup (×) and acceptance length τ. GSM8K/Math500/HumanEval serve purely as **prompt sets** for measuring generation speed; whether answers are correct is never measured or reported.
- Correction to what Lily told Andrew on the call: "they claim lossless because they can still pass these benchmarks" does not hold for DFlash — DFlash provides **no quality numbers at all**, not even pass rates. The argument is stronger than "benchmarks too narrow": SOTA spec-decoding papers don't consider quality something that needs measuring.

**Q5 — Do the prior papers (Leviathan, Medusa, EAGLE-3) contain the proof DFlash inherits?**
- [Leviathan et al. 2023](https://arxiv.org/abs/2211.17192): **the only formal proof in the lineage** (Appendix A.1) — speculative sampling with exact rejection sampling (accept if q≤p, else reject w.p. 1−p/q, resample from norm(max(0, p−q))) provably samples from p(x). Preconditions: exact rejection sampling + correct residual mass — exactly the two things later methods relax. Algorithm-correctness proof only; no empirical token-level verification even here.
- [Medusa 2024](https://arxiv.org/abs/2401.10774): **openly not lossless** — "typical acceptance" replaces rejection sampling with a dynamic probability threshold, explicitly trading distribution matching for acceptance rate; quality backed by GPT-4 scores (±0.07). The living example of Andrew's "they broke the preconditions".
- [EAGLE-3, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/file/c7b5a35ea98b62512a869c19ea7b03cb-Paper-Conference.pdf): **inherits explicitly and declines to measure**. Verbatim: "EAGLE-3 does not modify the target model's weights and uses strict speculative sampling acceptance conditions, ensuring no loss in performance. **Therefore, we do not evaluate generation quality.**" NeurIPS checklist self-reports "The paper does not include theoretical results [NA]". Metrics: speedup + τ only. Notably, they DO know the boundary — they exclude Medusa from temperature=1 comparisons because relaxed acceptance "do[es] not guarantee lossless acceleration".

**Lineage table (quotable for the article):**

| Paper | Proof | Quality measured / stance |
|---|---|---|
| Leviathan 2023 (theorem source) | Yes (Appendix A.1); preconditions: exact rejection sampling + residual mass | No |
| Medusa 2024 (openly not lossless) | No — explicitly relaxes (typical acceptance) | GPT-4 scores only |
| EAGLE-3 2025 (inheritance as methodology) | No (checklist: NA) | Explicitly declines: "we do not evaluate generation quality" |
| DFlash 2026 (word-level inheritance) | No; verification rule unstated | No (speedup + τ only) |

One-line thesis this supports: the losslessness proof was written once in 2023; every generation since either inherits it or openly relaxes it, and **no one has ever empirically verified it at the token level** — EAGLE-3 even codified not-measuring as methodology. The unchecked premise is that "strict acceptance conditions" remain strict in real implementations (DeepSeek's verification scheduling is a counterexample of engineering relaxation).

**The load-bearing observation for the article**: the loss is hard-label cross-entropy (one-hot response tokens), NOT a KL against the target's full-vocab distribution — training optimizes "mode correctness" and the loss weighting optimizes **acceptance length**, not distributional fidelity. Nothing in the training or architecture preserves the distribution; losslessness is entirely outsourced to a verification step whose rule the paper never specifies. This is the mechanistic backbone of Andrew's best-pet argument.

## Slack Feedback (structured, original wording preserved)

Andrew's written feedback around the call, reorganized by suggestion. Nothing summarized — his words verbatim, bulletized. Raw thread in the [sources file](20260903_andrew-conversation-debrief-sources.md).

### 1. Title: keep candidate 1 (anchor on "Speculative Decoding")

- [1:37 PM] "I'm sure you are working on this frantically ... so some early feedback (I'll get to the rest tonight)"
- [1:38 PM] "1) I like your current title more than your second one .... I think its important in a pedagogical article to hit the reader with the anchor/term that they will recognize ... here that is 'Speculative Decoding'"

### 2. Expand the first paragraph — back up, don't lose the audience

- [1:40 PM] "2) You need to expand your first paragraph or your audience will be too small. You need to take a few sentences and explain what speculative decoding is ... you need to start with why we need it (speeding up inference) and how it works (fast draft model + verification). As it is now .. you are too deep, too fast. You will lose anyone that doesn't know what 'draft' is in this context."
- [4:46 PM, after seeing the revised paragraph] "Yeah ... I think you need to back up ... you jump too far ahead ...if you start with 'speculative decoding decouples draft generation from target verification' you will loose a huge audience ... basically everyone who has heard the term but doesn't really know where it fits in the modern AI world or how it works"
- [4:50 PM] "You need to start with the idea that:"
  - "autoregressive decoding (at inference time) is a major bottleneck (up to you whether you want to get into the 'why')"
  - "speculative decoding was introduced in 2023 as an approach to accelerate inference"
  - "it works by leveraging a lighweight model to generate 'drafts' or short subsequences (a smaller model can do this more quickly) -- then using the full model to verify these drafts"
  - "importantly ... this procedure is *lossless*, but we'll get to what that means and why it is important (you want to set the hook)"
  - "if well aligned, this can speed up inference significantly -- because the draft + verifier combo is able to generate and accept sequence chunks rather than one token at a time."

### 3. Figure 1 animation

- [1:40 PM] "3) Is figure 1 going to be animated??"

### 4. De-jargon "What lossless means"

- [1:41 PM] "4) Your first paragraph in 'What lossless means' is too jargon heavy ... B200, SGLang, 'vanilla' in this context all require a lot of insider knowledge .. at the very least you might want to have a hover over glossery?"

### 5. Table 1: metric introduction order + non-integer τ

- [5:07 PM] "In table 1 ... you want to introduce your metrics in a sensible order ... for example ... you should introduce acceptance length (and \tau) before per-token latency (since you use \tau)"
- [5:08 PM] "in your example ... I'd be in favor of using a non-integer /tau as that seems unlikely ??"

### 6. LosslessBench "doesn't feel like it measures loss" (the thread that led to the call)

- [7:47 PM] "Yeah .. and its awesome ... but it doesn't feel like it measures loss"
- [7:48 PM] "I see it ... and again its great ... but loss (losslessness) here is a statistical distribution concept ..."
- [7:49 PM] "and so I would expect a measure of that property to be like the KL divergence (or similar) between some gob of output tokens ... or of logits"
- [7:50 PM] "how does this show they are lossy? you need some idea of what the variance or distribution is from the vanilla model?"
- [7:50 PM] "do you have a sec to talk .. might be easier?"

### 7. Section 3 notes (post-call, 8:30 PM)

- **Multimodal section — works, plus a token-density question:**
  - [8:31 PM] "The multimodal stuff makes a lot of sense -- its a nice well written section (sidenote is I think it might be some slight evidence towards my 'small models don't generalize as well' theory)"
  - "does the token density matter here? My understanding is that vision tokens carry a lot more information than text tokens ... as a result there just might not be as much juice to squeeze. I.e. its just a much harder problem to correctly predict a series of vision tokens."
- **Tool-call section — connect it back to CPU speculative execution:**
  - [8:33 PM] "The tool call stuff seems very reminiscent of CPU speculative execution (and branch prediction) .... which is really the origin of speculative decoding being called 'speculative' decoding"
  - "while the desired outcome is the same ... the approach needs to be very different ... much more like a CPU. We aren't just taking advantage of the parallelism of validation anymore"
- **Section 3.3 — cut it, end with a holistic conclusion:**
  - [8:37 PM] "3.3 doesn't seem to fit within the larger article ... I understand the trend here .... first it was quantization ... now its speculative decoding, but I think this section does more harm than good (the last thing the reader reads is the most tangential). I might replace it with a more holistic conclusion?"
  - [9:08 PM, Lily] "I agree with 3.3 doesn't seem to fit within the larger article , it is a bit odd, i can delete it" / "would you suggest just end with multimodal, drop the spec tool section too? @ahartnett" — **awaiting his reply**

## Transcript (cleaned)

#### Opening — ground rules

**Andrew:** I want to caveat this: I'm enjoying it very much. I'm providing criticism because that's what you need when you have twenty-four hours to make something better, not because I think it's bad.

**Lily:** No, the mean-teacher comments are the best. Let's talk about the LosslessBench idea.

#### What does "lossless" mean

**Lily:** I think I know what you're going for. Reading the article, "lossless" maybe leaves the impression of measuring something like a KL divergence or token log probability. I had considered that — host the model, get the token probability, compute the draft distribution and the target distribution. But that wouldn't work, because the target model only accepts the draft token when it aligns with the probability it can accept. So it wouldn't show anything.

> 💬 She anticipated his objection but dismissed the measurement as uninformative — the claim he spends the call overturning

**Andrew:** But I think that's what lossless means here.

**Lily:** I was hoping to define it as both: inference speed improved AND quality maintained. What I try to convey is that even though speed improved, we shouldn't expect quality degradation. Degradation can show at the token level or on a task.

**Andrew:** That's an argument you need to make. When we talk about being lossless, that's really a statement about the sampling probabilities for every token in the vocabulary being identical to those from the core distribution. You need to say that, and then say: we can measure that, but it might not be the most useful thing for someone building speculative decoding algorithms. What all these algorithm developments evidence is a Pareto frontier of inference acceleration with preservation of quality — we care less about the statistical guarantee than about utility and perceptual evaluation.

> ✅ The definition fix the article needs (9/10). State the statistical definition then pivot to utility explicitly | This became Top Suggestion #1

**Andrew:** You can argue this is obviously what companies are doing because of the sheer economics of speeding up inference 5x, and maybe they're over-indexing on a couple of small domains and need a wider set — which this provides. But one question: look at figure 11. If you asked the vanilla model to do this task 10 times, does it ever produce something like the flash? Does it ever mess up? Is the flash just one outcome from the vanilla model's own distribution, or has the introduced bias really degraded the quality?

> ⚠️ The sampling-vs-degradation challenge went unanswered (5/10). She pivoted to benchmark design instead of scoping the cheap 10-run experiment

**Lily:** You've brought up several points. First: the tasks here answer what people build speculative decoding for. Look at table 3 — EAGLE-3, DFlash, DSpark, DeepSpec — they test on very simple benchmarks like GSM8K and MATH, measuring speedup, acceptance length, and pass rate.

**Andrew:** But do they use that to make a claim of being lossless? That's not sufficient.

**Lily:** They claim they can pass all these benchmarks while gaining speedup.

**Andrew:** If I think about the speculative decoding story: it starts with the two original papers saying there's a free lunch — we can speed things up without any change to the statistics of our model. Then everybody said: great, except I don't want a 1.3x speedup, I want 6x. So they "relaxed" — broke — the preconditions that made it a free lunch. Now it's lossy. I'm surprised anybody uses pass rate on a benchmark to say they're lossless. I can see them using pass rate to say "we're lossy but it doesn't matter for the things you care about" — and maybe you want to say: pump the brakes, that claim isn't good, because 83% of what people do doesn't fall into these benchmarks. You're not speaking for me when you say nothing degrades on what I care about.

> ✅ The story arc handed over whole (9/10). Free lunch → relaxed preconditions → lossy, defended by a benchmark subset — the article's spine

#### The rejection-sampling equation

**Lily:** *(shares screen)* This equation effectively proves it's lossless — the final probability is equivalent to the target probability.

**Andrew:** That's only true if you're actually doing rejection sampling and correctly computing the residual mass. Your point is — scroll to figure 7 — in the effort to speed things up, they're relaxing exactly this. The middle panel is a form of lossless speculative decoding; the right panel is lossy. Companies roll out algorithms like the right bar and argue they still work for everything you care about. Your point is: no — they work for the small benchmarks, which don't represent the full distribution of tasks.

**Andrew:** A different way of saying it: if what I evaluate is whether the model still thinks the best pet is a dog, the model looks great — it says dog just as often as the full model. But that doesn't mean the distribution is the same. I'm not measuring whether it thinks the best pet is a cat. Your front-end development bench is the equivalent of asking "is the best pet a cat."

> ✅ The best-pet analogy (8/10). Pass-rate evals test the mode, not the distribution — a usable teaching line for the article

**Lily:** I thought about including relaxed thresholds in LosslessBench too, to show how lossy it gets. But there's a counterargument: deployment knobs are the provider's configuration choice, so relaxing them yourself is a subjective way to make inference lossy — people would say "you can't call DFlash lossy, you relaxed the rule yourself." What I want to show is that even as-served, DFlash — which claims lossless across everything — has lots of degradation on front-end design and creative writing, and people don't realize 83% of task domains are never tested by these acceleration algorithms.

> ✅ Solid defense of the as-served design choice (7/10). Objective degradation beats a knob-twiddling argument | Hurt: still hadn't engaged the distributional question

#### "I don't believe it's lossless"

**Andrew:** Maybe I'm being a hard-ass here, but I'm looking through the DFlash paper and I don't see anything I'd count as evidence that they're lossless. They say the word, but I see no quantitative substance.

**Lily:** They don't have evidence — the belief is pumped from the equation we just showed.

**Andrew:** Yeah. I don't believe it's lossless.

**Lily:** Okay. So you don't believe it's lossless — how do you want to convey that to the audience?

> ✅ Best question of the call (9/10). Flipped his skepticism into designing the fix instead of defending the framing

**Andrew:** I think you need to extract the logits for the whole vocabulary over a wide range of tasks and compute some sort of Bregman divergence — some distributional measure that says they're not the same.

**Andrew:** Maybe I'm being unfair, because you're responding in kind to the DFlash paper. But the story arc I see: speculative decoding came out with a theoretical reason to think it's lossless. Companies are making improvements because there's real economic value, assuming de facto that the original theoretical justification holds, without empirical verification. The limited signal they provide is just model performance on a subset of tasks. However, outside that set, there really is quality degradation.

**Andrew:** An example I think of: around 1992, NHTSA changed the set of crash tests required for new cars. In 1991 almost every car company had an A. In 1992, only about two companies passed — they had overfit to the specificities of a constructed test set. You're arguing that as companies hill-climb on speculative decoding algorithms, they're overfitting to a really limited test set. What it leaves us with is models that are fast and performative at coding and math but suffer real degradations on other tasks. What does that mean for you? If your task is outside those domains and you have knobs in your inference provider, you need to back off aggressive speculative decoding — you're paying for it even though DeepSeek isn't advertising that.

> ✅ NHTSA crash-test analogy gifted (9/10). A concrete historical precedent for benchmark overfitting, plus the practical reader takeaway

**Lily:** Good argument. But there are two levels of lossy. One: from the algorithm itself, even though it claims lossless — I'll do the log-probability computation between draft and target to know the gap concretely. Two: the overfitting issue — these models suck at front-end design and creative tasks; we're already eating the outcome, and I want to reveal that. Three: you can tune the knobs, but if the model itself is already lossy and overfit to coding and math, there isn't much room to play with. What we really want is awareness: when you train a faster model, be all-rounded and balanced instead of taking a shortcut.

> ✅ Live synthesis into her own structure (8/10). Committed to the token-level computation and restated the argument as two levels plus a takeaway

#### How draft models are trained

**Andrew:** Two things. One: I'm operating under the premise that the original two speculative decoding papers were in fact lossless — I don't know if that's entirely true.

**Lily:** I'm not sure either. They have the mathematical proof, but I don't know if they've done a comprehensive token-level computation.

**Andrew:** Two: we're trying to separate two effects. Models in general are overfitting to coding, science, and math — that's how RL post-training works. You want to argue speculative decoding is making that worse. But how is a speculative decoding model trained? Does it also go through RL post-training?

**Lily:** No RL — it's closer to SFT. Take a big Qwen model, pick a much smaller one, and train it to imitate the target model's token distribution. They use coding and math to validate that the token distributions match between draft and target.

> ✅ Held her ground on the training recipe (8/10). Filled his admitted intuition gap with the SFT-distillation recipe, DeepSpec repo, open weights, and dataset

**Andrew:** But why? If you're just training a small model to match a target distribution, you shouldn't care what the domain is — just generate whatever you want.

**Lily:** Without measuring, how do you know? Go to figure 11 and click replay — it shows the tokens generating in real time through vanilla, EAGLE-3, and DFlash. DFlash always posts "we're lossless and the fastest, we finished the task in 3.1 seconds" — but look, the generated output doesn't even work. Nobody checks that the calendar is ineffective. People look at the speed numbers.

**Andrew:** This seems well worth checking. But my point is I don't have good intuition for the training process. We more or less understand how base models are trained — pretraining, SFT, RL. All these speculative decoding methods have their own generative model inside — a small diffusion model, another LLM, whatever — and I don't know what its training recipe typically looks like.

**Lily:** DeepSeek open-sourced their recipe — DeepSpec — with the training and evaluation framework, the trained weights, and the dataset, whose distribution is again math, chat, and coding. I'll include a tutorial on how to train these models; I'm studying it now.

**Andrew:** Looking at that page under training: "train a draft model against cached target outputs" — what I'd assume, since you can generate infinite training data to estimate the target's distribution. So a couple of things could be going on. One: the base model has been over-trained on math and coding through RL on verifiable domains, and this looks like pretty vanilla distillation. One of the magics of a bigger model is generalization — if you distill down below that generalization threshold from an over-trained model, you could make the gap between math/coding and everything else even worse. Another: something is actually biased or broken in how the algorithm runs — like DeepSeek's verification scheduling peeking into the future and breaking assumptions. To me the story feels like: speculative decoding is supposed to be a free lunch; in practice it's really not. Show that it's not — real quality collapse in the domains that never get measured — and then: why?

> ✅ Two testable hypotheses for the why (9/10). Distillation below the generalization threshold vs broken algorithm mechanics — future-work section material

**Lily:** Answering why is very hard. Going down the math route, I'd have to prove mathematically why it's not lossless, and I don't know the answer. I can do the quality and token-level validation. I will definitely do the token-level computation and see if we find something concrete.

> ⚠️ The why-question was released instead of captured (5/10). His two hypotheses could have been claimed as the labeled future-work section
>
> 💡 Suggested: "If I can't prove the why, can I frame your two hypotheses as the future-work section and design one small experiment that distinguishes them?"

#### Tutorial scope and the Education track

**Lily:** Any recommendation for the last paragraph, the multimodal part?

**Andrew:** Sorry, I haven't gotten there — I'm in the hands-on lab.

> ⚠️ Asked about a section he had not read (4/10). One check-first question would have saved the turn

**Lily:** Do you think this tutorial is getting too deep? Lots of the questions you brought up are very good but beyond my reach.

**Andrew:** I don't know. I read the blog about what they're looking for and honestly the blurb didn't make sense to me — "we want articles about the reparametrization trick, but not about variational inference"? Those are both fairly straightforward mathematical things; the reparametrization trick isn't a trick, it's a mathematical identity. I didn't quite follow. Hopefully you submit, get useful feedback, look at what got accepted, and target again. High level: this is nicely wide-ranging — a review of the literature, an understanding of what's happening in practice, forward-looking future work, plus the hands-on. It's doing a lot of things. I don't know if that's what they want or if they want a Chris Olah-style super-focused interactive piece.

**Lily:** I'll email and ask them to confirm. I agree it has too much focus right now — I'll trim it down.

**Andrew:** I don't think they know either. They've decided to do this new track and they're going to figure it out on the fly.

**Lily:** I have confidence this will be accepted. I just don't know whether it will be the best — and that's fine.

> 💬 Confident close right after "nobody knows what they want" — endearing with a friend, but the verify-before-asserting pattern to watch in higher-stakes rooms

#### Wrap

**Lily:** Thank you, Andrew — I know it's super late. I really enjoyed the hard questions. I'll think more.

**Andrew:** No problem, Lily. This is really fun. I'll read the multimodal part real quick and then go to bed.
