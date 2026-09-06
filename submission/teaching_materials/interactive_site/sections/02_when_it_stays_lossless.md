<div id="notmean" class="section">

## 2. When it stays lossless

Section 1 covered how speculative decoding ensures lossless acceleration. In this section, we go through when that holds and when it does not: (2.1) lossless in papers, (2.2) lossless in deployment, and (2.3) a case study, LosslessBench, which measures losslessness on domains beyond math and coding.

</div>

<div id="papers" class="section" data-toc="2.1 Lossless in papers">

### 2.1 Lossless in papers

Even in the original papers, lossless is not unconditional. EAGLE-3 compares against Medusa only at temperature 0 but the relaxed acceptance variant is no longer lossless. This is because a method like Medusa is lossless depending on the temperature and on how strict the acceptance rule is:

- At temperature 0, decoding is deterministic: the target model selects its highest-probability next token, a draft token is accepted only when it matches, and it's lossless.
- At temperature 1, decoding is random: one position can have multiple valid answers. A method like Medusa accepts any draft tokens that clear a target probability threshold, so the mix of answers follows the draft's preference instead of the target's. The output distribution shifts and is no longer lossless ([Cai et al., 2024](https://arxiv.org/abs/2401.10774)).

Taking a prompt with two valid continuations: "The best pet is a \_\_\_". Say the target model assigns cat 0.5 and dog 0.5, and the draft model prefers dog:

- Rejection sampling: the draft proposes dog 80% of the time, but the target accepts only 5 out of 8 dog proposals (p/q = 0.5/0.8) and resamples the rest, so dog still comes out 50% of the time.
- A relaxed rule: every dog proposal that clears the threshold is accepted, so the output is biased toward the draft's favorite: the best pet becomes a dog with 0.8 probability. See Figure 10.

<figure>
<iframe src="../figures/figure7_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of rejection sampling and relaxed acceptance"></iframe>
</figure>
<figcaption><strong>Figure 10.</strong> Rejection sampling keeps the draft aligned with the target distribution. A relaxed rule follows the draft's preference.</figcaption>

Lossless also depends on how verification is scheduled. A poorly designed scheduler introduces selection bias. The acceptance rate improves while the output distribution has already shifted. This makes the inference no longer lossless. To be more specific, the scheduler decides whether draft token k gets verified, and that decision must depend on only the prefix through 1 to k-1. If the draft proposes token A at position k, followed by token B at position k+1, the scheduler cannot use B to decide whether to verify A. (See the Figure 11 example.)

<figure>
<iframe src="../figures/figure8_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of non-anticipating and peeking schedulers"></iframe>
</figure>
<figcaption><strong>Figure 11.</strong> Peeking at the token at k+1 creates selection bias.</figcaption>

DSpark ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) almost violated this non-anticipating rule. All prior methods rely on this precondition for their lossless claim to hold, but none of them tested whether the proof still holds when the precondition changes:

1. **The precondition.** As noted above, lossless speculative decoding requires non-anticipating admission: deciding whether to verify position k may use only the prefix through 1 to k - 1.
2. **What's wrong in DSpark's scheduler.** DSpark's scheduler ranks candidate draft tokens by their estimated probability of passing verification, then admits them one at a time while updating expected throughput. Scoring token k+1 from the preceding token k is ordinary. The problem arises because DSpark schedules the whole draft block jointly: its decision to admit token k can depend on the score of token k+1, and that score was computed from the proposed token k. The admission decision for k thus indirectly depends on k itself, violating non-anticipating admission, which the paper calls selection bias (Section 3.2.2, counterexample in Appendix A).
3. **DSpark's fix.** DSpark stops the search as soon as expected throughput declines. This makes the truncation decision depend only on the prefix processed so far, eliminating the selection bias.

<p class="pullquote">A relaxed acceptance rule or a peeking scheduler shifts the output distribution. In deployment, what else does losslessness depend on?</p>

</div>

<div id="deployment" class="section" data-toc="2.2 Lossless in deployment">

### 2.2 Lossless in deployment

In production, there are many configurations a user or company can adjust, and some of them decide whether decoding stays lossless. vLLM and SGLang, the two major engines, put it this way:

- **SGLang** keeps strict verification as the default: its acceptance thresholds ship at 1.0 ([SGLang docs](https://docs.sglang.ai/advanced_features/speculative_decoding.html)). A user can lower them to accept more tokens aggressively, and once they trade quality for speed this way, decoding is no longer lossless.
- **vLLM** splits losslessness into three layers ([vLLM docs](https://docs.vllm.ai/en/latest/features/speculative_decoding/)): (1) theoretical losslessness holds up to the precision limits of hardware numerics; (2) algorithmic losslessness is validated by convergence tests on the rejection sampler; (3) output stability is not promised. Layers 1 and 2 are covered by the paper's proof and the engine's tests, but layer 3 is not: a simple change in batch size can change logprobs, shifting the output distribution.

DSpark is a concrete example. When DeepSeek deployed it in production, the scheduler exposed two conflicts with real-world infrastructure ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147), Section 5.2), and they had to redesign around both to keep decoding lossless:

1. The algorithm assumes a smooth hardware capacity curve, but real GPU throughput is jagged. The fix is removing the early stop and searching over the whole jagged curve.
2. The algorithm decides how many draft tokens to verify at each step, but the serving engine needs the batch size to be fixed. The fix is scheduling asynchronously, using confidence predictions from two steps earlier to set the batch size. This also keeps the decision from seeing the current tokens, so the wider search in the first fix stays lossless.

Lastly, the production stack is complicated: it accelerates inference well beyond speculative decoding. Weights are <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-quantization">quantized<span class="glossary-tooltip" id="glossary-quantization" role="tooltip">Storing model weights with fewer bits to make inference faster and cheaper, sometimes with accuracy loss.</span></button> (lossy). <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-kv-cache">KV caches<span class="glossary-tooltip" id="glossary-kv-cache" role="tooltip">Stored attention information from earlier tokens that lets the model avoid recomputing the whole context.</span></button> are compressed (lossy). The serving system adds KV-cache-aware routing and prefill-decode disaggregation on top. With this many factors stacked together, whether the deployment as a whole is still lossless is hard to gauge.

Suppose a deployment gets everything above right: strict thresholds, a non-anticipating scheduler, a redesign for every engine constraint. How do we verify it still serves the end user's goal across all the different domains? Evidence for losslessness is limited to the domains where it was tested.

The state-of-the-art speculative decoding methods are all evaluated on: coding, chat, and mathematics. EAGLE-3, DFlash, and DSpark report acceptance length and speedup on GSM8K, MATH-500, AIME25, HumanEval, MBPP, LiveCodeBench, MT-Bench, Alpaca, and Arena-Hard. DeepSpec uses the same nine benchmarks (Table 3). These benchmarks cover only a small slice of real-world tasks. Outside them, the empirical evidence for losslessness is simply absent. Figure 12 shows the 29 task types in OpenRouter's real traffic ([OpenRouter, 2026](https://openrouter.ai/rankings)): the tested domains account for only 17% of token usage, and the other 83% has never been measured.

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
<iframe src="../figures/figure9_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated walkthrough of OpenRouter traffic by task type and speculative-decoding benchmark coverage"></iframe>
</figure>
<figcaption><strong>Figure 12.</strong> OpenRouter traffic by task type. 83% of tasks have never been measured by speculative decoding methods.</figcaption>

<p class="pullquote">So does lossless hold on the 83% domains/tasks that have never been measured?</p>

</div>

<div id="losslessbench" class="section">

### 2.3 Introducing Lossless Bench

The previous sections covered theoretical and algorithmic losslessness. To measure speculative decoding and inference acceleration on domains beyond coding and math, we built the [LosslessBench](https://lilyzh.ng/writing/losslessbench/).

**[LosslessBench](https://huggingface.co/datasets/lilyzhng/lossless_bench)** evaluates across five domains: coding, agent workflows, creative writing, guardrails, and frontend design. See Figure 14, each axis uses its domain's own benchmark and metric:

- Frontend: OpenDesign. Each page is judged twice: a GPT-4o vision judge scores the rendered screenshot on alignment, aesthetics, and structure, and a browser agent clicks every component to score whether the page actually works.
- Creative: EQ-Bench longform score, judged over multi-chapter creative writing.
- Guardrail: XSTest, classification accuracy on safe vs unsafe prompts built to sit near the decision boundary.
- Coding: Terminal-Bench pass rate.
- Agent workflow: tau3-bench long-horizon agent tasks, action match rate.

The benchmarks in these papers are simple, single-turn tasks such as grade-school math and function-level coding. They capture only a narrow slice of what models are asked to do in practice, which motivates the five domains above for LosslessBench.

Section 1 showed that a reported acceptance length is an implicit token-level divergence measurement, which makes it a natural probe for the five new domains (Figure 13). As a sanity check, our harness reproduces DFlash's published numbers on its own benchmarks: 5.32 vs. their 5.98 on GSM8K, and 5.96 vs. their 5.52 on HumanEval. Across the five LosslessBench axes, acceptance falls from 5.24 to 1.84. The draft drifts furthest on the domains the papers never measured. Frontend design is an exception: its acceptance stays high while the generated pages break (Figure 15), because acceptance measures draft and target agreement, not output quality. Whether the divergence translates into task-level quality loss is what Figure 14 examines.

<figure class="plain">
<img src="figures/fig_alpha_divergence.svg" alt="Two-panel bar chart: DFlash acceptance length by domain and the implied distributional divergence" />
</figure>
<figcaption><strong>Figure 13.</strong> DFlash acceptance length by domain (left) and the implied distributional divergence D_LK = 1 − α (right). Lower acceptance means larger token-level divergence.</figcaption>

<figure class="mid plain">
<img src="figures/fig_radar_spec_pilot.svg" alt="Radar chart of Qwen3-8B with vs without speculative decoding across five domains on LosslessBench" />
</figure>
<figcaption><strong>Figure 14.</strong> Qwen3-8B with vs without speculative decoding on LosslessBench. Axes are independently scaled, so each domain's relative gap is visible.</figcaption>

With the DFlash draft, frontend design drops from 54.5 to 45.5 and creative writing from 70 to 30. Guardrail holds at 80. Agentic workflow rises from 20.0 to 27.5. Both runs use the same Qwen3-8B with the same distribution, so the gain comes from the path each run happened to take. Under greedy decoding a small numerical difference flips one token; in an agent loop that flip can become an extra tool call, whose result changes every later turn. Across the ten tau3 retail tasks the accelerated run took that branch more often: it thinks longer (416 vs 261 words per thinking turn) and calls more tools (76 vs 54), and the extra tool results carry it to the higher score.

<p><strong>Explore the evaluation by yourself.</strong> Pick any domain and run the task:</p>
<p style="display:flex;gap:10px;flex-wrap:wrap;">
<a href="demo/compare_frontend.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Frontend Design</a>
<a href="demo/compare_taubench.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Agentic Workflow</a>
<a href="demo/compare_guardrail.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Safety Guardrail</a>
<a href="demo/compare_creative.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Creative Writing</a>
<a href="demo/compare_coding.html" target="_blank" style="padding:7px 18px;border:1.5px solid #1f5c3d;border-radius:999px;text-decoration:none;color:#1f5c3d;font-weight:600;">Agentic Coding</a>
</p>

<figure class="wide">
<iframe src="demo/race_demo.html" style="width:100%;height:720px;border:1px solid #ddd;border-radius:10px;" loading="lazy" title="Live decoding race on the calendar brief"></iframe>
</figure>
<figcaption><strong>Figure 15.</strong> The decoding race on the LosslessBench calendar brief (L101). Vanilla takes 18.7s, DFlash 8.9s. DFlash is the fastest, and its page is the broken one.</figcaption>

Look closely at Figure 15: the four models did not generate the same page, or even the same number of tokens. Vanilla produced 2,683 tokens on the calendar brief, the accelerated models between 2,606 and 3,048. DFlash decoded fastest per token (341 vs 143 tok/s), and its calendar came out visibly broken.

<figure class="wide">
<iframe src="demo/creative_race_demo.html" style="width:100%;height:720px;border:1px solid #ddd;border-radius:10px;" loading="lazy" title="Live decoding race on the creative brief"></iframe>
</figure>
<figcaption><strong>Figure 16.</strong> The same race on a 1000-word creative brief (LosslessBench L073). Vanilla takes 15.2s, DFlash 8.5s.</figcaption>


Figure 16 is the evaluation result on the creative writing task: EAGLE-3 and DSpark wrote identical stories, while vanilla and DFlash each took a different trajectory from the same opening line. That leaves three distinct stories to judge:

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

This section is a hands-on tutorial: adjust the acceptance threshold and watch what happens. A [Jupyter notebook walkthrough](https://github.com/lilyzhng/2026_NeurIPS_Education/blob/main/submission/teaching_materials/lab/lab_walkthrough.ipynb) covers every stage with the measured results embedded, so you can read the whole lab before spending GPU time.



</div>

<div id="servefirst" class="section">

#### a. Serve your first accelerated model

In this section you serve the same model twice, once vanilla and once with a speculator, and measure inference acceleration on your own GPU.

The checkpoints come from [DeepSpec](https://github.com/deepseek-ai/DeepSpec), which releases drafts for EAGLE-3, DFlash, and DSpark on the same target, Qwen3-8B. The serving engine is vLLM. The first deployment will have a cold start (image build plus a 16GB weight download, about 10 minutes), but it is cached afterwards, so later experiments are faster.

**Where to get the GPU.** Any H100/A100 works. If you don't have one, get \$30 free credits by signing up for a [Modal](https://modal.com) account. That covers this whole lab (an H100 is ~\$4/hour, a full afternoon uses \$8-12).

```bash
pip install modal && modal setup                    # one-time account link
git clone https://github.com/lilyzhng/2026_NeurIPS_Education && cd 2026_NeurIPS_Education/submission/teaching_materials/lab
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

Across 5 runs on one H100, the speedup is stable (mean ± std, Figure 17):

<figure class="mid">
<img src="figures/fig13_runs_h100.svg" alt="Bar chart: vanilla Qwen3-8B decodes 136.3 plus or minus 1.3 tok/s, with the DSpark draft 231.4 plus or minus 4.5 tok/s, a 1.70x speedup" />
</figure>
<figcaption><strong>Figure 17.</strong> Decode throughput of Qwen3-8B on one H100, vanilla vs with the DSpark draft. Mean ± std over 5 runs.</figcaption>

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

<div id="knobdemo" class="section">

#### b. Adjust acceptance rate yourself

SGLang ships with `--speculative-accept-threshold-single` at 1.0, where rejection sampling matches the target model. Lowering it accepts draft tokens more aggressively, trading losslessness for speed. We benchmarked 1.0 → 0.4 on the LosslessBench frontend design task (L101, the same calendar-popup prompt as Figure 15, temperature 1), regenerating the page at each stop and recording acceptance length and decode speed (Figure 18). At temperature 0 the threshold does nothing: every stop returned byte-identical pages.

<figure class="wide">
<iframe src="demo/knob_demo.html" style="width:100%;height:500px;border:1px solid #ddd;border-radius:10px;" loading="lazy" title="Interactive acceptance-threshold demo"></iframe>
</figure>
<figcaption><strong>Figure 18.</strong> The SGLang acceptance threshold on the LosslessBench frontend design task (L101, temperature 1).</figcaption>

At threshold 1.0 the verifier runs rejection sampling: the page follows the target model's distribution, whatever the draft proposes. Below 1.0 the lossless free lunch is gone: any draft token whose target probability clears the threshold is accepted without resampling, and the output drifts toward the draft. τ climbs from 4.9 to 7.2: 48% more draft-preferred tokens get through. The prompt asks for a stunning translucent calendar popup, judge each page with your own eyes.

</div>

<div id="race42" class="section">

#### c. The decoding race

In this section you watch four deployments race on the same prompt: the vanilla model against EAGLE-3, DFlash, and DSpark, all on H100. The point is to let the reader get a sense of what inference acceleration does on real-world tasks.

```bash
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
modal run modal_dflash_offline.py            # DFlash, see note below
python3 build_race_demo.py                   # assembles the demo from your outputs
```

These commands reproduce the two live demos in Section 2.3 (Figures 15 and 16).

<sub>Note: `vllm serve` crashes on DFlash in stable 0.28.0, and only the offline `LLM()` path is CI-tested, so `modal_dflash_offline.py` runs this way. Its draft is also the z-lab release rather than DeepSpec's.</sub>

</div>

<div id="fig11task" class="section">

#### d. Run LosslessBench on your own server

Let's use LosslessBench task L101: "Stunning translucent calendar popup that smoothly blends into the interface."

```bash
python3 generate_frontend_task.py --url <your-url> --label vanilla
```

Greedy decoding, so losslessness makes a concrete prediction: a speculator should reproduce the vanilla HTML exactly. Here is what we measured instead:

Run it twice, once on the vanilla server and once on the DSpark server, and compare the two HTML files:

<div class="table-wrap">
<table>
<thead>
<tr><th>Comparison</th><th>Identical prefix</th><th>First divergence</th><th>Final length</th></tr>
</thead>
<tbody>
<tr><td>vanilla vs DSpark</td><td>8,299 chars (76% of the page)</td><td><code>transition: color 0.2s</code> → <code>0.3s</code></td><td>10,924 vs 10,535 chars</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 5.</strong> The greedy byte-level comparison of the same L101 page, vanilla vs DSpark.</figcaption>

The rejection-sampling proof still holds at the algorithm level: it assumes both paths compute the same target probabilities. In practice the speculative path runs different kernels, the logits shift within floating-point precision, and a near-tie token (0.2s vs 0.3s here) falls the other way. Both pages render and satisfy the brief, and they are different pages: output stability is a separate layer, one that no engine promises (Section 2.2).

</div>

<div id="perdomainspeed" class="section">

#### e. Measure per-domain speed

The outputs vary by domain, and so does the speed. Measure each decoding method on the coding, creative, and frontend prompts with `race_domains.py`:

| domain | vanilla | DSpark | EAGLE-3 | DFlash |
|---|---|---|---|---|
| coding | 138.1 | 311.9 (2.3x) | 158.8 (1.15x) | 311.3 (2.25x) |
| creative | 138.2 | 416.7 (3.0x) | 229.5 (1.66x) | 265.6 (1.92x) |
| frontend | 137.6 | 333.1 (2.4x) | 208.2 (1.51x) | 274.0 (1.99x) |

**Table 6.** Decoding speed by domain: the same draft buys different speedups on different text.

As shown in Table 6, vanilla decodes at about 138 tok/s in every domain. The speculators' speed varies with the domain, because acceptance depends on how well the draft guesses that kind of text: DSpark reaches 3.0x on creative and 2.3x on coding. On this harness DSpark leads with acceptance length τ 3.5, DFlash follows at τ 2.2 to 2.5, and EAGLE-3 trails at τ 1.3.

Then the open exercise: swap in prompts from a domain nobody measured (OpenRouter's other 83%), rerun the race, and report three numbers together: acceptance rate, task correctness, domain coverage. LosslessBench samples 100 such tasks across the full OpenRouter distribution if you want a ready-made prompt set.

</div>
