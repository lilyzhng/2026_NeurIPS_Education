<div id="missed" class="section">

## 3 · What's Missed?

</div>

<div id="nevergrades" class="section">

### 3.1 · Eval Biased to Coding and Math Only

The nine datasets in Section 2.5 are not used the way their names suggest. In DeepSpec's `eval.py`, gsm8k and humaneval supply prompts, and the harness records four acceptance metrics per run: draft tokens per proposal, acceptance length, verify rate, and acceptance rate by position. It never checks whether the generated answer is correct. A search across the codebase finds no grader, no judge, no pass@1, no exact match, no accuracy metric of any kind. GSM8K is not a math test here. It is a traffic sample.

This means the lossless claim has never been directly verified even on math and coding. It rests entirely on the theorem from Section 2.2.

</div>

<div id="narrowroad" class="section">

### 3.2 · Why is it lossy in production?

The theorem guarantees exactness for one step: exact rejection-sampling verification against the target distribution. A production serving stack is longer than that. Quantized weights and KV caches, cache-aware routing, prefill-decode disaggregation, and relaxed acceptance rules all sit outside the proof's assumptions. vLLM's own documentation describes its typical-acceptance mode as trading response quality for speed ([vLLM docs](https://docs.vllm.ai/en/latest/features/spec_decode.html)).

The gap between theory and stack shows up in measurement. In [LosslessBench](https://lilyzh.ng/posts/losslessbench/), the same GLM 5.2 model served through a vendor's accelerated stack (fp4, speculative decoding, kv routing, prefill-decode disaggregation) lost 5.6 points on frontend design tasks, 76.9 to 71.2, relative to the reference deployment. Kimi K3, whose acceleration is trained and shipped by the model owner, lost 0.3 points on the same evaluation. Both deployments would report healthy acceptance rates. Only one of them preserved behavior.

</div>

<div id="knob" class="section">

### 3.3 · Acceptance rate is not accuracy

The flag that breaks the assumption ships in the official code. DeepSpec's evaluation exposes `--confidence-threshold`: when the draft's confidence exceeds the threshold, verification stops early and the remaining draft tokens are accepted without being checked. This is the lossless-for-speed trade in a single flag.

The experiment is direct. Run the same prompts across a sweep of thresholds, record acceptance metrics the way the harness already does, and additionally grade the outputs for task correctness. As the threshold loosens, acceptance climbs and task accuracy falls.

<div class="tbd"><span class="tag">TBD · Original results</span>Trade-off curve, acceptance
      rate vs task accuracy across the confidence-threshold sweep. This is the core original
      figure.</div>

Acceptance rate is not accuracy, and after this sweep the learner has seen the two numbers move in opposite directions on the same model and the same prompts.

</div>

<div id="mismatch" class="section">

### 3.4 · The verified domains are not the used domains

Who actually hits these accelerated endpoints, and with what? Public usage data from OpenRouter's model rankings ([openrouter.ai/rankings](https://openrouter.ai/rankings)) shows that programming is large but far from alone: roleplay and creative writing, marketing copy, translation, and agentic workflows account for a substantial share of real traffic. The verification effort, meanwhile, concentrates on math and code.

The mismatch has a mechanical reason to matter. Acceptance rate is domain-conditional. Code and math are low-entropy, the draft guesses well, and acceptance is high. Creative and open-ended text is high-entropy, and acceptance drops. The domains where verification is densest are exactly the domains where acceleration is least likely to misbehave. Providers validate where it is easy, users live where it is not, and the expectation gap between the two is the hole this article is pointing at.

<div class="tbd"><span class="tag">TBD</span>Figure: OpenRouter usage share by category next
      to the domain coverage of current speculative-decoding evals.</div>

</div>

<div id="losslessbench" class="section">

### 3.5 · Introducing LosslessBench

LosslessBench is our answer to the question. [LosslessBench](https://lilyzh.ng/posts/losslessbench/) runs the same task suite against a reference deployment and an accelerated deployment of the same model, across five domains: coding, agent workflows, creative writing, guardrails, and frontend design. Each pair of outputs is graded for task behavior, not for token overlap.

The headline finding: frontend design lost 5.6 points under the accelerated stack while four of the five domains showed no significant gap. The degradation is domain-localized, which is exactly what acceptance-rate reporting cannot see. The failure is also qualitative, not cosmetic:

<figure>
<div class="fig2">
<img src="https://lilyzh.ng/posts/losslessbench/id673_fp8.png" alt="fp8 render of the calendar prompt, with the requested translucent popup implemented" /> <img src="https://lilyzh.ng/posts/losslessbench/id673_fp4.png" alt="fp4 render of the same prompt, a clean page with the calendar popup missing" />
</div>
<figcaption><strong>Figure 2.</strong> The same model, the same frontend prompt, two deployments. The reference deployment (left) implements the requested translucent calendar popup. The accelerated fp4 deployment (right) ships a clean-looking page with the requested component missing.</figcaption>
</figure>

</div>

<div id="scope" class="section">

### 3.6 · Scope statement

Two limits. First, the lossless theorem is distribution-level, not sequence-level. Even under exact verification at temperature 1, an individual output can differ from what the reference deployment would have produced; the guarantee is that outputs are drawn from the same distribution, not that any single generation matches. Second, all numbers in this article are measured at batch size 1 and low concurrency. Under high concurrency speculative decoding degrades and serving engines may disable it entirely, so production behavior at load is a separate question from everything measured here.

> **Summary.** The standard evaluation harness never grades outputs; the lossless claim rests on a theorem, not on measurement. The theorem covers exact verification only, and the measured gap between owned and vendor-assembled acceleration is 0.3 vs 5.6 points. A single flag in the official evaluation code converts lossless into lossy, and the resulting curve is measurable by a learner in an afternoon. Verification concentrates where acceptance is naturally highest; real usage concentrates elsewhere.

</div>
