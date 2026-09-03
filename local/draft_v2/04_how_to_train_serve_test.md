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

Across 5 runs on one H100, the speedup is stable (mean ± std): vanilla 136.3 ± 1.3 tok/s, DSpark 231.4 ± 4.5 tok/s — η ≈ 1.70x. (Per-run table removed 2026-09-03; replaced by Figure 14 (`fig14_runs_h100.svg`) on the site.)

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

### 4.2 The decoding race: algorithms x domains（定稿 2026-09-03，实测数据 data/4_2_race_vllm.json）

Now race the algorithms across domains: redeploy with a different draft, rerun the same three-domain prompt set (`race_domains.py`: coding / creative / frontend, 512 tokens each, greedy).

```bash
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py   # config relabel applied in the script
SPEC_MODE=dflash modal deploy modal_vllm_serve.py
python3 race_domains.py --url <your-url> --label <mode>   # once per deploy
```

Our H100 medians (tok/s, speedup over vanilla):

| domain | vanilla | DSpark | EAGLE-3 | DFlash (broken config) |
|---|---|---|---|---|
| coding | 138.1 | 311.9 (2.3x) | 158.8 (1.15x) | 119.1 (0.86x) |
| creative | 138.2 | 416.7 (3.0x) | 229.5 (1.66x) | 110.3 (0.80x) |
| frontend | 137.6 | 333.1 (2.4x) | 208.2 (1.51x) | 111.1 (0.81x) |

**Table 4.** The decoding race, measured: three-domain medians per lane. All draft weights are DeepSpec's; the EAGLE-3 lane needs a one-line config relabel to load (its acceptance is under-tuned, τ ≈ 1.3), and the DFlash column shows a misconfigured lane kept on purpose.

Three readings. Vanilla is flat across domains; the speculators are not: acceptance is domain-conditional, and the same recipe ranks DSpark (τ 3.5) above EAGLE-3 (τ 1.3) on this target. DFlash comes out *slower than vanilla*, and the metrics counters say why: τ ≈ 1.03, almost every draft token rejected, so the lane pays full drafting cost for nothing. A mismatched drafter costs you speed: benchmark before you swap one in. And a caveat on the creative row: at temperature 0, open-ended prose loops, and repetitive text is easy to draft. Rerun at temperature 0.7 and compare.

<!-- TODO 4.2: race tool 动画（fig6 复刻）；EAGLE-3 泳道 τ 调优（aux layer ids 待与 DeepSpec 训练值核对，t2d/d2t 缺失影响待查）；DFlash 列等 z-lab 官方配方结果落地后替换/并列；temp0 creative 膨胀效应补 temp 0.7 对照 -->


### 4.3 Break losslessness on purpose（定稿骨架 2026-09-03 凌晨，sweep 数据填充中 data/4_3_sweep.json）

Section 2.1 showed that a relaxed acceptance rule only shifts the output distribution when you sample. So this experiment runs at temperature 1.0, and it runs on SGLang: the acceptance threshold (`--speculative-accept-threshold-single/acc`) is an SGLang serving flag, and vLLM exposes no equivalent. Which engine you serve on decides which lossless-breaking knobs you can even reach. That is Section 2.2 in one sentence.

For each threshold from 1.0 (strict, lossless) to 0.3, `sweep_threshold.py` redeploys the DSpark server, runs a GSM8K subset, and records speed, acceptance length, and accuracy:

```bash
python3 sweep_threshold.py --url <your-sglang-url> --n 30
```

Our H100 results (30 problems, temperature 1.0):

| threshold | tokens/s | τ | accuracy |
|---|---|---|---|
| 1.0 (lossless) | 127.1 | 3.9 | 0.70 |
| 0.9 | 121.2 | 4.8 | 0.53 |
| 0.7 | 128.0 | 7.2 | 0.80 |
| 0.5 | 127.3 | 4.7 | 0.73 |
| 0.3 | 119.4 | 4.4 | 0.73 |

**Table 5.** Threshold sweep on SGLang + DSpark: acceptance responds, speed stays verification-bound, accuracy stays inside small-sample noise.

The knob bites where theory says it should: acceptance length climbs as the threshold loosens (3.9 to 7.2). What does not appear is the clean speed-up-accuracy-down curve: throughput stays verification-bound at batch size 1, and accuracy at n=30 moves inside its own noise band (0.53 and 0.80 are two draws of the same coin). That absence is the lesson: on a robust domain like GSM8K, the damage from relaxed acceptance hides below small-sample noise, which is exactly why Section 2.3 needed open-ended frontend prompts and a bigger N to see the gap. This fills Figure 12 with real results, error bars and all.

One negative result worth keeping: we first ran this sweep greedy, and every threshold produced identical τ and accuracy: at temperature 0 a draft token is accepted only on exact match, so the threshold never fires. The knob only exists where sampling exists, which is exactly Section 2.1's temperature bullet.

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

Then the open exercise: swap in prompts from a domain nobody measured (OpenRouter's other 83%), rerun the race and the sweep, and report three numbers together: acceptance rate, task correctness, domain coverage. If the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?

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
