<div id="notmean" class="section">

## 2. What it doesn't mean

Section 1 proved lossless in theory: verification ensures the output distribution is aligned with the target model's. But when does it hold or not hold? In this section we go through the boundary of that guarantee: (2.1) what lossless doesn't mean in papers, (2.2) speculative decoding in production, and (2.3) a case study, LosslessBench, which measures losslessness on domains beyond math and coding.

</div>

<div id="papers" class="section">

### 2.1 What lossless doesn't mean in papers

Even in the original papers, lossless is not unconditional. EAGLE-3 compares against Medusa only at temperature 0 but the relaxed acceptance variant drops the lossless guarantee. This is because a method like Medusa is lossless depending on the temperature and on how strict the acceptance rule is:

- At temperature 0, decoding is deterministic: the target model selects its highest-probability next token, a draft token is accepted only when it matches, and it's lossless.
- At temperature 1, decoding is random: one position can have multiple valid answers. A method like Medusa accepts any draft tokens that clear a target probability threshold, so the mix of answers follows the draft's preference instead of the target's. The output distribution shifts and is no longer lossless ([Cai et al., 2024](https://arxiv.org/abs/2401.10774)).

Taking a prompt with two valid continuations: "The best pet is a \_\_\_". Say the target model assigns cat 0.5 and dog 0.5, and the draft model prefers dog:

- Rejection sampling: the draft proposes dog 80% of the time, but the target accepts only 5 out of 8 dog proposals (p/q = 0.5/0.8) and resamples the rest, so dog still comes out 50% of the time.
- A relaxed rule: every dog proposal that clears the threshold is accepted, so the output is biased toward the draft's favorite: the best pet becomes a dog with 0.8 probability. See Figure 7.

<figure>
<img src="figures/fig7_pet_distribution.png" alt="Rejection sampling keeps the target's 50/50 cat-dog mix; a relaxed threshold rule shifts the output to the draft's 80/20 preference" />
</figure>
<figcaption><strong>Figure 7 (mock).</strong> Rejection sampling keeps the target's mix; a relaxed rule follows the draft's.</figcaption>

Lossless also depends on how verification is scheduled. A poorly designed scheduler introduces selection bias. The acceptance rate improves while the output distribution has already shifted. This makes the inference no longer lossless. To be more specific, the scheduler decides whether draft token k gets verified, and that decision must depend on only the prefix through 1 to k-1. If the draft proposes token A at position k, followed by token B at position k+1, the scheduler cannot use B to decide whether to verify A. (See the Figure 8 example.)

<figure>
<img src="figures/fig7_peeking.png" alt="A scheduler peeking at the token at position k+1 to decide whether to verify position k" />
</figure>
<figcaption><strong>Figure 8 (mock).</strong> Peeking at the token at k+1.</figcaption>

DSpark ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) almost violated this non-anticipating rule. All prior methods rely on this precondition for their lossless claim to hold, but none of them tested whether the proof still holds when the precondition changes:

1. **The precondition.** As noted above, lossless speculative decoding requires non-anticipating admission: deciding whether to verify position k may use only the prefix through 1 to k - 1.
2. **What's wrong in DSpark's scheduler.** DSpark's scheduler ranks candidate draft tokens by their estimated probability of passing verification, then admits them one at a time while updating expected throughput. Scoring token k+1 from the preceding token k is ordinary. The problem arises because DSpark schedules the whole draft block jointly: its decision to admit token k can depend on the score of token k+1, and that score was computed from the proposed token k. The admission decision for k thus indirectly depends on k itself, violating non-anticipating admission, which the paper calls selection bias (Section 3.2.2, counterexample in Appendix A).
3. **DSpark's fix.** DSpark stops the search as soon as expected throughput declines. This makes the truncation decision depend only on the prefix processed so far, eliminating the selection bias.

<u>Algorithmic losslessness holds only with careful handling: a relaxed acceptance rule or a peeking scheduler shifts the output distribution, and DSpark caught its own case. We need to be more careful when deploying the spec models. So in deployment, what else does the lossless guarantee depend on?</u>

</div>

<div id="deployment" class="section">

### 2.2 Lossless in the paper does not mean lossless in deployment

In production, there are many configurations a user or company can adjust, and some of them affect the lossless guarantee. vLLM and SGLang, the two major engines, put it this way:

- **SGLang** keeps strict verification as the default: its acceptance thresholds ship at 1.0 ([SGLang docs](https://docs.sglang.ai/advanced_features/speculative_decoding.html)). A user can lower them to accept more tokens aggressively, and once they trade quality for speed this way, lossless is no longer guaranteed.
- **vLLM** splits losslessness into three layers ([vLLM docs](https://docs.vllm.ai/en/latest/features/speculative_decoding/)): (1) theoretical losslessness holds up to the precision limits of hardware numerics; (2) algorithmic losslessness is validated by convergence tests on the rejection sampler; (3) output stability is not guaranteed. Layers 1 and 2 are covered by the paper's proof and the engine's tests, but layer 3 is not: a simple change in batch size can change logprobs, shifting the output distribution.

DSpark is a concrete example. When DeepSeek deployed it in production, the scheduler exposed two conflicts with real-world infrastructure ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147), Section 5.2), and they had to redesign around both to keep the lossless guarantee:

1. The algorithm assumes a smooth hardware capacity curve, but real GPU throughput is jagged. The fix is removing the early stop and searching over the whole jagged curve.
2. The algorithm decides how many draft tokens to verify at each step, but the serving engine needs the batch size to be fixed. The fix is scheduling asynchronously, using confidence predictions from two steps earlier to set the batch size. This also keeps the decision from seeing the current tokens, so the wider search in the first fix stays lossless.

Lastly, the production stack is complicated: it accelerates inference well beyond speculative decoding. Weights are quantized (lossy). KV caches are compressed (lossy). The serving system adds KV-cache-aware routing and prefill-decode disaggregation on top. With this many factors stacked together, whether the deployment as a whole is still lossless is hard to gauge.

Suppose a deployment gets everything above right: strict thresholds, a non-anticipating scheduler, a redesign for every engine constraint. How do we verify it still serves the end user's goal across all the different domains? Evidence for losslessness is limited to the domains where it was tested.

The state-of-the-art speculative decoding methods are all evaluated on: coding, chat, and mathematics. EAGLE-3, DFlash, and DSpark report acceptance length and speedup on GSM8K, MATH-500, AIME25, HumanEval, MBPP, LiveCodeBench, MT-Bench, Alpaca, and Arena-Hard. DeepSpec uses the same nine benchmarks (Table 3). These benchmarks cover only a small slice of real-world tasks. Outside them, the empirical evidence for losslessness is simply absent. Figure 9 shows the 29 task types in OpenRouter's real traffic ([OpenRouter, 2026](https://openrouter.ai/rankings)): the tested domains account for only 17% of token usage, and the other 83% has never been measured.

<div class="table-wrap">
<table>
<thead>
<tr><th>Method</th><th>Math</th><th>Code</th><th>Chat / instruction</th><th>Other</th></tr>
</thead>
<tbody>
<tr><td>EAGLE-3 (2025)</td><td>GSM8K</td><td>HumanEval</td><td>MT-Bench, Alpaca</td><td>CNN/Daily Mail (summarization)</td></tr>
<tr><td>DFlash (2026)</td><td>GSM8K, MATH-500, AIME25</td><td>HumanEval, MBPP, LiveCodeBench</td><td>MT-Bench, Alpaca</td><td>—</td></tr>
<tr><td>DSpark (2026)</td><td>GSM8K, MATH-500, AIME25</td><td>HumanEval, MBPP, LiveCodeBench</td><td>MT-Bench, Alpaca, Arena-Hard</td><td>DeepSeek-V4 live traffic (speed only)</td></tr>
<tr><td>DeepSpec harness</td><td>gsm8k, math500, aime25</td><td>humaneval, mbpp, livecodebench</td><td>mt-bench, alpaca, arena-hard-v2</td><td>—</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 3.</strong> Where lossless was measured. Evaluation datasets in each paper's experiment section.</figcaption>

<figure>
<img src="figures/fig8_openrouter_treemap.png" alt="Treemap of OpenRouter traffic by task type: the domains tested by speculative decoding papers cover 17% of token usage" />
</figure>
<figcaption><strong>Figure 9 (mock).</strong> OpenRouter traffic by task type. 83% of tasks have never been measured by spec methods.</figcaption>

<u>So does lossless hold on the 83% domains/tasks that have never been measured?</u>

</div>

<div id="losslessbench" class="section">

### 2.3 Case study: LosslessBench

The previous sections covered theoretical and algorithmic losslessness. To measure speculative decoding and inference acceleration on domains beyond coding and math, we built the [LosslessBench](https://lilyzh.ng/writing/losslessbench/).

**LosslessBench** takes one model, serves it twice, once without acceleration and once with. It evaluates across five domains: coding, agent workflows, creative writing, guardrails, and frontend design. See Figure 10, each axis uses its domain's own benchmark and metric:

- Frontend: OpenDesign, 100 prompts. Each generated page is rendered in a real browser, and a GPT-4o vision judge scores the screenshot on instruction alignment, aesthetics, and structure.
- Creative: EQ-Bench longform score, judged over multi-chapter creative writing.
- Guardrail: XSTest, classification accuracy on safe vs unsafe prompts built to sit near the decision boundary.
- Coding: Terminal-Bench pass rate.
- Agent workflow: tau3-bench long-horizon agent tasks, action match rate.

<figure class="mid">
<img src="figures/fig9_radar_five_domains.png" alt="Radar chart of GLM 5.2 quality across five domains, original vs accelerated serving" />
</figure>
<figcaption><strong>Figure 10.</strong> GLM 5.2 quality across five domains. Axes are independently scaled, so each domain's relative gap is visible.</figcaption>

We identified a significant gap in the frontend design evaluation under a vendor-assembled stack (fp4 quantization, speculative decoding, KV routing, prefill-decode disaggregation): the same GLM 5.2 model lost 5.6 points, 76.9 to 71.2. Design output is open-ended and hard for a draft to predict. It is absent from the speculative decoding benchmarks. However, frontend and UI tasks carry significant weight in the OpenRouter task usage (Figure 9). In other words, users would receive degraded performance when they use spec models tuned for coding and math only. Figure 11 shows one failure: the accelerated deployment renders a clean page and omits the component the prompt asked for. The other four domains showed no significant gap.

<figure>
<div class="fig2">
<img src="https://lilyzh.ng/writing/losslessbench/id673_fp8.png" alt="reference render of the calendar prompt, with the requested translucent popup implemented" /> <img src="https://lilyzh.ng/writing/losslessbench/id673_fp4.png" alt="accelerated render of the same prompt, a clean page with the calendar popup missing" />
</div>
</figure>
<figcaption><strong>Figure 11.</strong> The same model, the same frontend prompt, left is the original model, right is with inference acceleration.</figcaption>

We also designed an experiment to show that relaxing an acceptance parameter can lead to degradation. DeepSpec exposes a confidence threshold; we sweep it from strict to loose, and observe task accuracy difference at each step.

<figure>
<img src="figures/fig11_threshold_sweep.png" alt="Task accuracy as the DeepSpec confidence threshold is relaxed from strict to loose" />
</figure>
<figcaption><strong>Figure 12 (mock, TBD original results).</strong> Threshold sweep: task accuracy from strict to loose acceptance.</figcaption>

</div>
