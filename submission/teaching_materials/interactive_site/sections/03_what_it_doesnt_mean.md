<div id="notmean" class="section">

## 2. What it doesn't mean

Section 1 proved lossless in theory: verification ensures the output distribution is aligned with the target model's. But when does it hold or not hold? In this section we go through the boundary of that guarantee: (2.1) what lossless doesn't mean in papers, (2.2) speculative decoding in production, and (2.3) a case study, LosslessBench, which measures losslessness on domains beyond math and coding.

</div>

<div id="papers" class="section" data-toc="2.1 What it doesn't mean in papers">

### 2.1 What lossless doesn't mean in papers

Even in the original papers, lossless is not unconditional. EAGLE-3 compares against Medusa only at temperature 0 but the relaxed acceptance variant drops the lossless guarantee. This is because a method like Medusa is lossless depending on the temperature and on how strict the acceptance rule is:

- At temperature 0, decoding is deterministic: the target model selects its highest-probability next token, a draft token is accepted only when it matches, and it's lossless.
- At temperature 1, decoding is random: one position can have multiple valid answers. A method like Medusa accepts any draft tokens that clear a target probability threshold, so the mix of answers follows the draft's preference instead of the target's. The output distribution shifts and is no longer lossless ([Cai et al., 2024](https://arxiv.org/abs/2401.10774)).

Taking a prompt with two valid continuations: "The best pet is a \_\_\_". Say the target model assigns cat 0.5 and dog 0.5, and the draft model prefers dog:

- Rejection sampling: the draft proposes dog 80% of the time, but the target accepts only 5 out of 8 dog proposals (p/q = 0.5/0.8) and resamples the rest, so dog still comes out 50% of the time.
- A relaxed rule: every dog proposal that clears the threshold is accepted, so the output is biased toward the draft's favorite: the best pet becomes a dog with 0.8 probability. See Figure 7.

<figure>
<iframe src="../figures/figure7_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of rejection sampling and relaxed acceptance"></iframe>
</figure>
<figcaption><strong>Figure 7.</strong> Rejection sampling keeps the target's mix; a relaxed rule follows the draft's.</figcaption>

Lossless also depends on how verification is scheduled. A poorly designed scheduler introduces selection bias. The acceptance rate improves while the output distribution has already shifted. This makes the inference no longer lossless. To be more specific, the scheduler decides whether draft token k gets verified, and that decision must depend on only the prefix through 1 to k-1. If the draft proposes token A at position k, followed by token B at position k+1, the scheduler cannot use B to decide whether to verify A. (See the Figure 8 example.)

<pre><code>NON-ANTICIPATING (lossless)           PEEKING SCHEDULER (selection bias)

draft:  [t1]..[tk-1] [tk] [tk+1]      draft:  [t1]..[tk-1] [tk] [tk+1]
              |       ?                             |        ?     |
verify tk? ---+                       verify tk? ---+              |
uses prefix 1..k-1 only                  ... but also the score of tk+1,
                                         which was computed FROM tk
decision independent of tk               admission of tk depends on tk itself
=&gt; output distribution preserved      =&gt; output distribution shifts</code></pre>
<figcaption><strong>Figure 8 (mock).</strong> Peeking at the token at k+1.</figcaption>

DSpark ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) almost violated this non-anticipating rule. All prior methods rely on this precondition for their lossless claim to hold, but none of them tested whether the proof still holds when the precondition changes:

1. **The precondition.** As noted above, lossless speculative decoding requires non-anticipating admission: deciding whether to verify position k may use only the prefix through 1 to k - 1.
2. **What's wrong in DSpark's scheduler.** DSpark's scheduler ranks candidate draft tokens by their estimated probability of passing verification, then admits them one at a time while updating expected throughput. Scoring token k+1 from the preceding token k is ordinary. The problem arises because DSpark schedules the whole draft block jointly: its decision to admit token k can depend on the score of token k+1, and that score was computed from the proposed token k. The admission decision for k thus indirectly depends on k itself, violating non-anticipating admission, which the paper calls selection bias (Section 3.2.2, counterexample in Appendix A).
3. **DSpark's fix.** DSpark stops the search as soon as expected throughput declines. This makes the truncation decision depend only on the prefix processed so far, eliminating the selection bias.

<u>Algorithmic losslessness holds only with careful handling: a relaxed acceptance rule or a peeking scheduler shifts the output distribution, and DSpark caught its own case. We need to be more careful when deploying the spec models. So in deployment, what else does the lossless guarantee depend on?</u>

</div>

<div id="deployment" class="section" data-toc="2.2 Lossless in deployment">

### 2.2 Lossless in deployment

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

<pre><code>OPENROUTER TRAFFIC BY TASK TYPE (29 task types, share of token usage)

+---------------------+------------------------------------------------+
| TESTED BY SPEC      |  NEVER MEASURED                          83%   |
| PAPERS        17%   |                                                |
|                     |  frontend / UI      marketing     legal        |
|  coding   math      |  creative writing   translation   roleplay     |
|  chat / instruction |  agent workflows    medical       data extract |
|                     |  ...and 19 more task types                     |
+---------------------+------------------------------------------------+</code></pre>
<figcaption><strong>Figure 9 (mock).</strong> OpenRouter traffic by task type. 83% of tasks have never been measured by spec methods.</figcaption>

<u>So does lossless hold on the 83% domains/tasks that have never been measured?</u>

</div>

<div id="losslessbench" class="section">

### 2.3 Introducing Lossless Bench

The previous sections covered theoretical and algorithmic losslessness. To measure speculative decoding and inference acceleration on domains beyond coding and math, we built the [LosslessBench](https://lilyzh.ng/writing/losslessbench/).

**[LosslessBench](https://huggingface.co/datasets/lilyzhng/lossless_bench)** evaluates across five domains: coding, agent workflows, creative writing, guardrails, and frontend design. See Figure 11, each axis uses its domain's own benchmark and metric:

- Frontend: OpenDesign. Each page is judged twice: a GPT-4o vision judge scores the rendered screenshot on alignment, aesthetics, and structure, and a browser agent clicks every component to score whether the page actually works.
- Creative: EQ-Bench longform score, judged over multi-chapter creative writing.
- Guardrail: XSTest, classification accuracy on safe vs unsafe prompts built to sit near the decision boundary.
- Coding: Terminal-Bench pass rate.
- Agent workflow: tau3-bench long-horizon agent tasks, action match rate.

The benchmarks in these papers are simple, single-turn tasks such as grade-school math and function-level coding. They capture only a narrow slice of what models are asked to do in practice, which motivates the five domains above for LosslessBench.

Section 1 showed that a reported acceptance length is an implicit token-level divergence measurement. That makes it a natural probe for the five new domains (Figure 10). As a sanity check, our harness reproduces DFlash's published numbers on its own benchmarks: 5.32 vs. their 5.98 on GSM8K, and 5.96 vs. their 5.52 on HumanEval. Across the five LosslessBench axes, however, acceptance falls from 5.24 to 1.84. The draft distribution drifts furthest exactly on the domains the papers never measured. Frontend design is an instructive exception: its acceptance stays high while the generated pages break (Figure 12), a reminder that acceptance measures draft and target agreement, not output quality. Whether the divergence translates into task-level quality loss is what Figure 11 examines.

<figure class="plain">
<img src="figures/fig_alpha_divergence.svg" alt="Two-panel bar chart: DFlash acceptance length by domain and the implied distributional divergence" />
</figure>
<figcaption><strong>Figure 10.</strong> DFlash acceptance length by domain (left) and the implied distributional divergence D_LK = 1 − α (right). Lower acceptance means larger token-level divergence.</figcaption>

<figure class="mid plain">
<img src="figures/fig_radar_spec_pilot.svg" alt="Radar chart of Qwen3-8B with vs without speculative decoding across five domains on LosslessBench" />
</figure>
<figcaption><strong>Figure 11.</strong> Qwen3-8B with vs without speculative decoding on LosslessBench. Axes are independently scaled, so each domain's relative gap is visible.</figcaption>

<p><strong>Explore the evaluation by yourself.</strong> Pick any domain and run the task:</p>
<p style="display:flex;gap:10px;flex-wrap:wrap;">
<a href="compare_frontend.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Frontend Design</a>
<a href="compare_taubench.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Agentic Workflow</a>
<a href="compare_guardrail.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Safety Guardrail</a>
<a href="compare_creative.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Creative Writing</a>
<a href="compare_coding.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Agentic Coding</a>
</p>

<figure class="wide">
<iframe src="race_demo.html" style="width:100%;height:720px;border:1px solid #ddd;border-radius:10px;" loading="lazy" title="Live decoding race on the calendar brief"></iframe>
</figure>
<figcaption><strong>Figure 12.</strong> The decoding race on the LosslessBench calendar brief (L101). Vanilla takes 18.7s, DFlash 8.9s.</figcaption>

<figure class="wide">
<iframe src="creative_race_demo.html" style="width:100%;height:720px;border:1px solid #ddd;border-radius:10px;" loading="lazy" title="Live decoding race on the creative brief"></iframe>
</figure>
<figcaption><strong>Figure 13.</strong> The same race on a 1000-word creative brief (LosslessBench L073). Vanilla takes 15.2s, DFlash 8.5s.</figcaption>

Look closely at Figure 12: the four lanes did not generate the same page, or even the same number of tokens. Vanilla produced 2,683 tokens on the calendar brief, the accelerated lanes between 2,606 and 3,048. DFlash decoded fastest per token (341 vs 143 tok/s), and its calendar came out visibly broken.

Figure 13 is the evaluation result on the creative writing task: EAGLE-3 and DSpark wrote identical stories, while vanilla and DFlash each took a different trajectory from the same opening line. That leaves three distinct stories to judge:

| story | instruction following | Latin vocabulary | writing style |
|---|---|---|---|
| vanilla · 7/10 | 979 words. Ends entering the fight, close to violating the no-combat rule. | Correct, restrained. | Strongest sensory detail. Named cast. Ending falls back on a generic freedom monologue. |
| EAGLE-3 / DSpark · 6/10 | Best. 998 words, all constraints met. | Correct, sparse. | Weakest as fiction. Restates one thesis three times. No named characters. Explains politics rather than dramatizing it. |
| DFlash · 7.5/10 | Worst. 1,092 words, 9% over. Invents a sacrae bell. | Inaccurate, decorative. | Best structure. Full dawn-to-night arc, one side character with a backstory, strongest closing image. |

**Table 4.** The three distinct gladiator stories, judged on the brief's own constraints. Same target model, greedy decoding: the differences are trajectory divergence, not different models.

Overall, DFlash wins. Fiction lives on shape and character before compliance, and DFlash is the only story that delivers a complete day, a side character you remember, and a closing image that lands. Its violations are copyedit-level fixes. EAGLE-3 and DSpark followed every rule and produced the piece you forget first.

Interestingly, DFlash wrote the worst calendar page but the best story. Why do EAGLE-3 and DSpark match in writing and front end code, while DFlash stands apart? EAGLE-3 and DSpark share DeepSpec's training data, propose similar tokens. DFlash differs in training data, block size, and serving path, so the exact cause cannot be ruled out here, but likely caused by the difference in training data.

</div>

<div id="train" class="section">

### 2.4 Hands-On Lab

The last three sections drew the boundary of the lossless evidence. This one hands you the tools to test it yourself.

</div>

<div id="servefirst" class="section">

#### Serve your first accelerated model

In this section you serve the same model twice, once vanilla and once with a speculator, and measure inference acceleration on your own GPU.

The checkpoints come from [DeepSpec](https://github.com/deepseek-ai/DeepSpec), which releases drafts for EAGLE-3, DFlash, and DSpark on the same target, Qwen3-8B. The serving engine is vLLM. The first deployment will have a cold start (image build plus a 16GB weight download, about 10 minutes), but it is cached afterwards, so later experiments are faster.

**Where to get the GPU.** Any H100/A100 works. If you don't have one, get $30 free credits by signing up for a [Modal](https://modal.com) account. That covers this whole lab (an H100 is ~$4/hour, a full afternoon uses $8-12).

```bash
pip install modal && modal setup                    # one-time account link
git clone https://github.com/lilyzhng/2026_NeurIPS_Education && cd */teaching_materials/lab
SPEC_MODE=vanilla modal deploy modal_vllm_serve.py   # prints your server URL
```

The script pins the image, caches model weights in a volume so they download once, and exposes the server at a public URL. When done, `modal app stop neurips-spec-lab` releases the GPU.

Serve the vanilla model:

```bash
vllm serve Qwen/Qwen3-8B --port 8000
```

Send a prompt and measure the generation speed (`measure_decoding_speed.py`). Then restart the server with the DeepSpec DSpark speculator (on Modal: `SPEC_MODE=dspark modal deploy modal_vllm_serve.py`) and run the same bench again:

```bash
vllm serve Qwen/Qwen3-8B --port 8000 --speculative-config \
  '{"model": "deepseek-ai/dspark_qwen3_8b_block7", "method": "dspark", "num_speculative_tokens": 7}'
```

Across 5 runs on one H100, the speedup is stable (mean ± std, Figure 13):

<figure class="mid">
<img src="figures/fig13_runs_h100.svg" alt="Bar chart: vanilla Qwen3-8B decodes 136.3 plus or minus 1.3 tok/s, with the DSpark draft 231.4 plus or minus 4.5 tok/s, a 1.70x speedup" />
</figure>
<figcaption><strong>Figure 13.</strong> Decode throughput of Qwen3-8B on one H100, vanilla vs with the DSpark draft. Mean ± std over 5 runs.</figcaption>

vLLM does not report acceptance length or per-token latency directly. Both come from real measurements: latency from the throughput above, and τ from the server's `/metrics` counters (5,180 draft tokens proposed at 7 per pass = ~740 verification passes for 2,606 generated tokens). See the calculation below:

<div class="sptc-py" data-lang="text"><pre>
L_target = 1 / 136.3 tok/s ≈ 7.3 ms         # latency of the target (vanilla) model, per token
L_dspark = 1 / 231.4 tok/s ≈ 4.3 ms         # latency with the DSpark draft, per token
τ        ≈ 3.5                             # acceptance length
&nbsp;
T_draft + T_verify = L_dspark × τ ≈ 15.1 ms # cost of one draft+verify pass
η = L_target / L_dspark ≈ 1.70x             # speedup
</pre></div>

</div>

<div id="race42" class="section">

#### The decoding race

In this section you watch four deployments race on the same prompt: the vanilla model against EAGLE-3, DFlash, and DSpark, all on H100. The point is to let the reader get a sense of what inference acceleration does on real-world tasks.

```bash
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
modal run modal_dflash_offline.py            # DFlash lane, see note below
python3 build_race_demo.py                   # assembles the demo from your outputs
```

These commands reproduce the two live demos in Section 2.3 (Figures 11 and 12).

<sub>Note: `vllm serve` crashes on DFlash in stable 0.28.0, and only the offline `LLM()` path is CI-tested, so `modal_dflash_offline.py` runs this way. Its draft is also the z-lab release rather than DeepSpec's.</sub>

</div>
