# 4. Hands-On Lab

<!-- 定位（Round 29 → 2026-09-02 wavemind 重设计）：读者复现正文的结果。组织原则一句话："every exercise fills in one of the article's own blanks" — 没有一个练习是为了动手而动手。SGLang serving（8/23 决定弃 vLLM），DeepSpec 现成 checkpoints（EAGLE-3 / DFlash / DSpark，Qwen3-4B/8B/14B + Gemma），target 用 Qwen3-8B 对齐 Section 1 的 230 tok/s → 2.3x 数字。不加 multimodal（VLM 对比只做 optional 脚注）。设计讨论全文：Thoughts/artifacts/20260902-neurips-section4-handson-design.md -->

<!-- 作者任务（先于写正文，见 wavemind Promises 0902-1~4）：
  [ ] 真跑宠物采样实验（strict vs relaxed, 1000 samples）→ 真图替换 §2.1 Figure 7（作者作业，不是 lab 练习）
  [ ] 真跑 threshold sweep → Figure 12 真实结果（替换 TBD）
  [ ] 补 spec-decoding-only 的 before/after 对比（§2.3 TODO，现 Figure 11 是 quantization 退化）
  [ ] 真跑通 4.1（DeepSpec checkpoint + SGLang 拉起验证），跑图脚本 = lab starter code，一鱼两吃
-->

## 定稿（4.1-4.4, 2026-09-02/03; H100 实测数据见 data/）

### 4.1 Serve your first accelerated model

In this section you serve the same model twice, once vanilla model and once with a speculator, and measure inference acceleration on your own GPU.

The checkpoints come from [DeepSpec](https://github.com/deepseek-ai/DeepSpec), which releases drafts for eagle 3, dflash and dspark on the same target, Qwen3-8B. The serving engine is vLLM. The first deployment will have cold start (image build plus a 16GB weight download, about 10 minutes). But it is cached afterwards, so later experiments would be faster.

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

Across 5 runs on one H100, the speedup is stable (mean ± std): vanilla 136.3 ± 1.3 tok/s, DSpark 231.4 ± 4.5 tok/s — η ≈ 1.70x. (Per-run table removed 2026-09-03; replaced by Figure 16 (`fig14_runs_h100.svg`) on the site.)

vLLM does not report acceptance length or per-token latency directly. Both come from our measurements: latency from the throughput above, and τ from the server's `/metrics` counters (5,180 draft tokens proposed at 7 per pass = ~740 verification passes for 2,606 generated tokens). See the calculation below:

```text
L_target = 1 / 136.3 tok/s ≈ 7.3 ms         # latency of the target (vanilla) model, per token
L_dspark = 1 / 231.4 tok/s ≈ 4.3 ms         # latency with the DSpark draft, per token
τ        ≈ 3.5                             # acceptance length
&nbsp;
T_draft + T_verify = L_dspark × τ ≈ 15.1 ms # cost of one draft+verify pass
η = L_target / L_dspark ≈ 1.70x             # speedup
```

<!-- 作者注(不面向读者,2026-09-03 实测): 三个 DeepSpec checkpoint 只有 DSpark 双引擎可服。EAGLE-3 两边都挂(SGLang 无 Qwen3 形状 eagle3 类;vLLM 报 weights [4096,20480] vs config [4096,12288] shape mismatch,疑 checkpoint 发布件 bug,待提 issue)。DFlash SGLang 拒载(markov_rank=0),vLLM relabel 后可载但 τ≈1.03 draft 全拒(4.2 表里 0.8x 的原因)。4.3 用 SGLang 因为只有它有 accept-threshold 旋钮。 -->

<!-- 设计稿存档(2026-09-02): 叙事弧 = 先爽(serve/race)、再打脸(threshold twist)、最后开放(unmeasured domain);依赖链零重复搭建;race tool 贯穿;预算 ~2h 单卡兑现 §2.3 承诺。 -->

### 4.2 The decoding race（定稿重写 2026-09-03，文风对齐 4.1）

In this section you watch four deployments race on the same prompt: the vanilla model against EAGLE-3, DFlash, and DSpark, all on H100. The point is to let the reader get a sense of what inference acceleration does on real-world tasks.

```bash
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
modal run modal_dflash_offline.py            # DFlash lane, see note below
python3 build_race_demo.py                   # assembles the demo from your outputs
```

These commands reproduce the two live demos in Section 2.3 (Figures 11 and 12).

Look closely at Figure 11 in Section 2.3: the four lanes did not generate the same page, or even the same number of tokens. Vanilla produced 1,282 tokens on the calendar brief, the accelerated lanes 1,127 to 1,185. DFlash finished fastest, and its calendar came out visibly broken.

Figure 12 is the evaluation result on the creative writing task: EAGLE-3 and DSpark wrote identical stories, while vanilla and DFlash each took a different trajectory from the same opening line. That leaves three distinct stories to judge:

| story | instruction following | Latin vocabulary | writing style |
|---|---|---|---|
| vanilla · 7/10 | 979 words. Ends entering the fight, close to violating the no-combat rule. | Correct, restrained. | Strongest sensory detail. Named cast. Ending falls back on a generic freedom monologue. |
| EAGLE-3 / DSpark · 6/10 | Best. 998 words, all constraints met. | Correct, sparse. | Weakest as fiction. Restates one thesis three times. No named characters. Explains politics rather than dramatizing it. |
| DFlash · 7.5/10 | Worst. 1,092 words, 9% over. Invents a sacrae bell. | Inaccurate, decorative. | Best structure. Full dawn-to-night arc, one side character with a backstory, strongest closing image. |

**Table 4.** The three distinct gladiator stories, judged on the brief's own constraints. Same target model, greedy decoding: the differences are trajectory divergence, not different models.

Overall, DFlash wins. Fiction lives on shape and character before compliance, and DFlash is the only story that delivers a complete day, a side character you remember, and a closing image that lands. Its violations are copyedit-level fixes. EAGLE-3 and DSpark followed every rule and produced the piece you forget first.

The cross-domain twist: DFlash wrote the worst calendar page and the best story. A lane's trajectory can land well in one domain and badly in another, and nothing in the serving stack tells you which you got.

Why do EAGLE-3 and DSpark match in writing and front end code, while DFlash stands apart? EAGLE-3 and DSpark share DeepSpec's training data, propose similar tokens. DFlash differs in training data, block size, and serving path, so the exact cause cannot be ruled out here, but likely caused by the difference in training data.

<sub>Note: `vllm serve` crashes on DFlash in stable 0.28.0, and only the offline `LLM()` path is CI-tested, so `modal_dflash_offline.py` runs this way. Its draft is also the z-lab release rather than DeepSpec's.</sub>

<!-- TODO 4.2: demo 页面 race_demo.html / creative_race_demo.html 在 local/draft_v2/demo/，上线待 Lily 批准；EAGLE-3 τ 调优；Figure 15 旧图已撤，待重绘或废弃 -->

<!-- 作者注：DFlash 翻案时间线（9/3）：serve 崩 → enforce-eager 证伪 → 官方离线配方一次通过（trust_remote_code + spec max_model_len 32768 为 serve 缺失字段，Hypothesis）。τ≈2.54 由 counters 反推。旧 broken 列存档：coding 119.1 / creative 110.3 / frontend 111.1，DeepSpec relabel τ≈1.03，见 failures.md R5/R6/R10。 -->

<!-- 4.3 parked: see parked_4_3_threshold_sweep.md (redesign queued: frontend A/B) -->

### 4.4 The Figure 11 task, on your own server（定稿 2026-09-03，data/4_4_frontend/）

Section 2.3 found its frontend gap under a full vendor stack, where quantization was the culprit. Here you isolate one variable: speculative decoding alone, on the same brief Figure 11 used (OpenDesign id 673, "Stunning translucent calendar popup that smoothly blends into the interface").

```bash
python3 generate_frontend_task.py --url <your-url> --label vanilla   # rerun per lane
```

Greedy decoding, so the lossless guarantee makes a concrete prediction: a speculator should reproduce the vanilla HTML exactly. Here is what we measured instead:

```text
vanilla vs dspark:  identical for 8,299 chars (76% of the page),
                    then diverges at one CSS value:
                    transition: color 0.2s   ->   transition: color 0.3s
                    and the trajectories separate from there (10,924 vs 10,535 chars)
```

This is not the theorem failing. The guarantee is about distributions, not trajectories: the speculative path runs different kernels, the numerics shift by a hair, and a near-tie token (0.2s vs 0.3s was evidently one) falls the other way. vLLM's own docs drew this boundary in Section 2.2: theoretical losslessness holds "up to the precision limits of hardware numerics," and output stability is layer three, the one nobody guarantees. Both pages render, both satisfy the brief, and they are different pages. If your product depends on reproducing an exact output, lossless-in-distribution is not the property you think it is.

Speed has the same domain dependence as the outputs. The per-domain rates (`race_domains.py`, one prompt per domain, 512 tokens, greedy, median of 5 repeat runs):

| domain | vanilla | DSpark | EAGLE-3 | DFlash |
|---|---|---|---|---|
| coding | 138.1 | 311.9 (2.3x) | 158.8 (1.15x) | 311.3 (2.25x) |
| creative | 138.2 | 416.7 (3.0x) | 229.5 (1.66x) | 265.6 (1.92x) |
| frontend | 137.6 | 333.1 (2.4x) | 208.2 (1.51x) | 274.0 (1.99x) |

**Table 5.** Per-domain decoding rates, tokens per second. One prompt per domain, so this is a probe of domain-conditional acceptance, not a benchmark. DSpark and EAGLE-3 use DeepSpec drafts on `vllm serve`. DFlash uses the z-lab draft on the offline path, which carries slightly less HTTP overhead.

Vanilla is flat across domains, the speculators are not: acceptance is domain-conditional, so the same draft buys different speedups on different text (DSpark: 3.0x on creative, 2.3x on coding). The ranking is recipe-dependent too: DSpark (τ 3.5) leads, DFlash (τ 2.2 to 2.5, domain-dependent) follows, EAGLE-3 trails (τ 1.3, under-tuned in our relabeled config rather than at its ceiling). A caveat on the creative row: at temperature 0, open-ended prose loops, and repetitive text is easy to draft. Rerun at temperature 0.7 and compare.

Then the open exercise: swap in prompts from a domain nobody measured (OpenRouter's other 83%), rerun the race, and report three numbers together: acceptance rate, task correctness, domain coverage. LosslessBench samples 100 such tasks across the full OpenRouter distribution if you want a ready-made prompt set. If the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?

### 贯穿件与呈现格式

- race tool：4.1 单人版 → 4.2 三人版 → 4.3 加 accuracy 泳道。
- 网页格式统一：命令块（深绿 pre）→ expected output → 一行 callout "this fills Figure/Table X"。
- optional 脚注：vLLM 已 merge Qwen2.5-VL 的 EAGLE-3（§3.1），想验证 multimodal acceptance drop 的读者可自行尝试；不进主线（显存/时长破坏 one-GPU 承诺）。

## 旧版素材（原 Hands-on Lab 全文，vLLM 版，已被上方设计稿取代；保留命令与 model card 数字作参考）

> <div id="runit" class="section">
> 
> ## 5 · Hands-on Lab
> 
> Serve and verify a draft model on your own. One GPU is enough.
> 
> ### 5.1 · Serve an accelerated model
> 
> One command starts Qwen3-8B with its official EAGLE-3 draft head:
> 
>     vllm serve Qwen/Qwen3-8B -tp 1 \
>       --speculative-config '{"model": "RedHatAI/Qwen3-8B-speculator.eagle3",
>                              "num_speculative_tokens": 3, "method": "eagle3"}'
> 
> Send it a few prompts and read the acceptance metrics vLLM logs per request. The [model card](https://huggingface.co/RedHatAI/Qwen3-8B-speculator.eagle3) reports an acceptance length of 2.4 to 2.8 on a single A100; your numbers should land in that range on coding prompts and lower on open-ended ones. That difference is Section 3.4 showing up on your own hardware.
> 
> ### 5.2 · Compare three generations of drafts (Section 2.3)
> 
> [DeepSpec](https://github.com/deepseek-ai/DeepSpec) releases trained checkpoints for EAGLE-3, DFlash, and DSpark on the same targets (Qwen3-4B/8B/14B), so the three-generation comparison needs no training. Point the evaluation at each checkpoint in turn and compare acceptance length on the same prompt set.
> 
> <div class="tbd"><span class="tag">TBD</span>Exact commands and our measured table.</div>
> 
> ### 5.3 · Sweep the confidence threshold (Section 3.3)
> 
> Using the DeepSpec evaluation harness, sweep `--confidence-threshold` over a range of values on gsm8k prompts. For each run, keep the generated answers and grade them for correctness in a separate pass. Plot acceptance rate against task accuracy.
> 
> <div class="tbd"><span class="tag">TBD</span>Sweep script and grading script, with the
>       resulting curve.</div>
> 
> ### 5.4 · Exercise: pick a domain nobody measured
> 
> Swap the prompt set for one outside math and code, creative writing, an agent trace, or a frontend task, and rerun 5.1. Watch what happens to acceptance length, then ask the question this article ends on: if the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?
> 
> </div>
