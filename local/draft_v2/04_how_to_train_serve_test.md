# 4. How to Train, Serve, and Test It

<!-- 定位（Round 29 → 2026-09-02 wavemind 重设计）：读者复现正文的结果。组织原则一句话："every exercise fills in one of the article's own blanks" — 没有一个练习是为了动手而动手。SGLang serving（8/23 决定弃 vLLM），DeepSpec 现成 checkpoints（EAGLE-3 / DFlash / DSpark，Qwen3-4B/8B/14B + Gemma），target 用 Qwen3-8B 对齐 Section 1 的 230 tok/s → 2.3x 数字。不加 multimodal（VLM 对比只做 optional 脚注）。设计讨论全文：Thoughts/artifacts/20260902-neurips-section4-handson-design.md -->

<!-- 作者任务（先于写正文，见 wavemind Promises 0902-1~4）：
  [ ] 真跑宠物采样实验（strict vs relaxed, 1000 samples）→ 真图替换 §2.1 Figure 7（作者作业，不是 lab 练习）
  [ ] 真跑 threshold sweep → Figure 12 真实结果（替换 TBD）
  [ ] 补 spec-decoding-only 的 before/after 对比（§2.3 TODO，现 Figure 11 是 quantization 退化）
  [ ] 真跑通 4.1（DeepSpec checkpoint + SGLang 拉起验证），跑图脚本 = lab starter code，一鱼两吃
-->

## 定稿（4.1 written 2026-09-02; numbers from our H100 runs, see data/4_1_bench.json）

### 4.1 Serve your first accelerated model

Everything in Sections 1 through 3 can be reproduced on one GPU. In this section you will serve the same model twice, once plain and once with a speculator, and watch the three deciding factors from Table 1 show up in your own terminal.

We use SGLang as the serving engine and the [DeepSpec](https://github.com/deepseek-ai/DeepSpec) checkpoints, which cover all three algorithms from Section 1 (EAGLE-3, DFlash, DSpark) on the same target models, so no training is needed. The target is Qwen3-8B, the same model as Section 1's walkthrough. One note on hardware: our numbers below are from one H100, and Section 1's walkthrough is a B200. Numbers scale with your GPU; the ratios are what should match.

**Launch first, read while it warms.** The first deployment pays a one-time cold start (image build plus a 16GB weight download, about 10 minutes). Start it now and keep reading; both are cached afterwards.

**Where to get the GPU.** Any box with one H100/A100 works. If you don't have one: get $30 free credits by signing up for a [Modal](https://modal.com) account — that covers this whole lab (an H100 is ~$4/hour, and the full afternoon uses $8-12). Our lab repo ships a ready launch script — three commands, no infra to write:

```bash
pip install modal && modal setup                    # one-time account link
git clone https://github.com/lilyzhng/2026_NeurIPS_Education && cd */teaching_materials/lab
SPEC_MODE=vanilla modal deploy modal_sglang_serve.py   # prints your server URL
```

The script pins the image, caches the model weights in a volume so you download them once, and exposes the server at a public URL. When you're done for the day, `modal app stop neurips-lab-sglang` releases the GPU.

Under the hood (or on your own machine) the vanilla server is one SGLang command:

```bash
python3 -m sglang.launch_server --model-path Qwen/Qwen3-8B \
  --host 0.0.0.0 --port 30000 --mem-fraction-static 0.85 --enable-metrics
```

Send it the same passage Figure 1 decodes and time the generation (our `bench_41.py` does this: one warmup, then five timed runs of 512 tokens):

```text
[vanilla] run 0: 3.65s, 512 tokens, 140.4 tok/s
[vanilla] run 4: 3.61s, 512 tokens, 141.8 tok/s
median: 140.7 tok/s        # your number scales with your GPU
```

Now restart the server with the DeepSpec DSpark speculator attached — the same speculator DeepSeek runs in production (Section 1.3), and the same server Section 4.3's threshold sweep will reuse. This is the only change:

```bash
python3 -m sglang.launch_server --model-path Qwen/Qwen3-8B \
  --host 0.0.0.0 --port 30000 --mem-fraction-static 0.85 --enable-metrics \
  --speculative-algorithm DSPARK \
  --speculative-draft-model-path deepseek-ai/dspark_qwen3_8b_block7
```

(With the Modal script: `SPEC_MODE=dspark modal deploy modal_sglang_serve.py`.)

Run the same bench again. Our H100 run:

```text
[dspark] run 0: 2.32s, 512 tokens, 220.6 tok/s
[dspark] run 4: 2.38s, 512 tokens, 215.4 tok/s
median: 215.6 tok/s                       # 1.53x over our own baseline
sglang:spec_accept_length τ = 2.9         # from /metrics
sglang:spec_accept_rate    = 0.27
```

That 1.53x on conversational text sits where the DSpark paper's own 60-85% per-user gains predict, on the low end because open-ended prose is harder to draft than code — Section 2's domain point, already visible in exercise one.

**Close the loop with Table 1's formula.** You now hold measured values of every quantity Section 1 defined. Per-token latency is `L = 1 / (tokens per second)`: the vanilla run gives `L_target = 7.1 ms`, the speculative run gives `L = 4.6 ms`. Table 1 says `L = (T_draft + T_verify) / τ`, so the combined draft-plus-verify cost per verification pass is `L × τ = 4.6 × 2.9 ≈ 13.5 ms` — nearly twice a vanilla forward pass, but it emits 2.9 tokens instead of one. That is the whole trade in one line: pay ~1.9 forward passes, get 2.9 tokens, net `η = L_target / L = 1.53x`. This fills Figure 1 with your own lanes.

**A compatibility note you will hit if you swap checkpoints.** The DeepSpec DSpark checkpoint loads natively in SGLang (its `Qwen3DSparkModel` architecture is registered in the engine, which was built to read DeepSpec checkpoints). The DeepSpec EAGLE-3 checkpoint uses an architecture registered in vLLM instead, and the DeepSpec DFlash checkpoint carries the DSpark architecture tag with the Markov head disabled, which SGLang's DSpark loader rejects (`markov_rank=0`) — for a DFlash lane, use the official [z-lab drafters](https://huggingface.co/z-lab/Qwen3-8B-DFlash-b16). Engine support is part of what "production-ready" means for a speculator: Section 1.5 made this point with a table, and here it decides what you can serve tonight.

**Close the loop with Table 1's formula.** You now hold measured values of the quantities Section 1 defined. Per-token latency is `L = 1 / (tokens per second)`, so the vanilla run gives `L_target = ⟨L_TARGET⟩ ms` and the speculative run gives `L = ⟨L_SPEC⟩ ms`. The formula `L = (T_draft + T_verify) / τ` then tells you the combined draft-plus-verify cost per verification pass: `T_draft + T_verify = L × τ = ⟨T_SUM⟩ ms`, against a single vanilla forward pass of `⟨L_TARGET⟩ ms`. The speedup you measured, `η = L_target / L = ⟨SPEEDUP⟩`, is the same number Table 1's definition predicts. This fills Figure 1 with your own lanes.

> **Sidebar: feel it in two commands first.** Production platforms package this whole section behind one flag. On [Fireworks](https://docs.fireworks.ai/deployments/speculative-decoding), dedicated deployments ship with a default drafter already attached: `firectl deployment create <model> --wait` serves an accelerated model, and `--disable-speculative-decoding` gives you the baseline for comparison. A five-minute detour if you want the feeling before the mechanics; the SGLang server you started above is the one the rest of this lab builds on.

## 设计稿（2026-09-02 定 — 4.2-4.4 待跑通后成文）

叙事弧照正文 Section 1 → 2 → 2.3 的情绪曲线排：**先爽（serve、race）、再打脸（threshold twist）、最后开放（unmeasured domain）**。依赖链零重复搭建：4.1 的 server 被 4.2 复用，4.2 的 DSpark config 被 4.3 复用，4.4 复用全部。race tool 贯穿三节逐步加泳道。总预算 ~2h 单卡，兑现 §2.3 的 "a single afternoon and one GPU"。

### 4.1 Serve your first accelerated model（SGLang，~20 min）

- 做什么：SGLang 两条命令 — 先 vanilla Qwen3-8B，再挂 DeepSpec 的 EAGLE-3 checkpoint。同一段文本各跑一遍，记录 tokens/s、τ、T_draft、T_verify。
- 产出：race tool 单人版（vanilla vs spec 两条泳道）= 个人版 Figure 1；再用 Table 1 公式亲手算 η，和实测对账（复现 Section 1 的数学 walkthrough）。
- 填的空：Figure 1 的个人复现。
- TBD：SGLang 命令（替换旧版 vLLM 命令）、实测数字范围。

### 4.2 The decoding race: algorithms x domains（定稿 2026-09-02，实测数据 data/4_2_race.json）

The server you started is one lane. Now race the algorithms across domains: redeploy with a different draft, rerun the same three-domain prompt set (`bench_race.py`: coding / creative / frontend, 512 tokens each, greedy).

```bash
SPEC_MODE=dspark modal deploy modal_sglang_serve.py   # DeepSpec checkpoint
SPEC_MODE=dflash DRAFT_MODEL=z-lab/Qwen3-8B-DFlash-b16 modal deploy modal_sglang_serve.py
python3 bench_race.py --url <your-url> --label <mode>   # once per deploy
```

Our H100 medians (tok/s, speedup over vanilla):

| domain | vanilla | DSpark | DFlash |
|---|---|---|---|
| coding | 133.7 | 278.0 (2.1x) | 293.6 (2.2x) |
| creative | 131.8 | 354.4 (2.7x) | 482.9 (3.7x) |
| frontend | 131.7 | 294.1 (2.2x) | 386.1 (2.9x) |

Vanilla is flat across domains; the speculators are not — acceptance is domain-conditional, and the spread between columns is Section 1's architecture story in your own numbers. One caveat before you over-read the creative row: at temperature 0, open-ended prose tends to loop, and repetitive text is easy to draft. Rerun that lane at temperature 0.7 and watch the gap change — that observation is exercise 4.4 in miniature.

<!-- TODO 4.2: race tool 动画（fig6 复刻）+ EAGLE-3 泳道（需 SGLang 格式 Qwen3-8B checkpoint，DeepSpec 的是 vLLM 格式）；temp0 creative 膨胀效应写正文前先补 temp 0.7 对照 -->


### 4.3 Break losslessness on purpose（~30 min，反转）

- 前菜（5 min）：同一 prompt，batch size 1 vs 32，diff logprobs — 亲眼验证 vLLM layer-3 "output stability is not guaranteed"（§2.2）。
- 正菜：DeepSpec `--confidence-threshold` 从 1.0 拧到 0.3，每档跑小 task set（gsm8k 子集），另跑一个 grading pass 记 accuracy。plot acceptance vs accuracy。
- 产出：真实 Figure 12（speed 上行、accuracy 下行）。
- 填的空：Figure 12。放在 race 之后才有戏剧性：刚庆祝完速度，现在看代价。
- TBD：sweep 脚本 + grading 脚本 + 曲线。

### 4.4 Exercise: pick a domain nobody measured（open-ended homework）

- 做什么：从 OpenRouter 那 83% 里挑一个域，写 20 条 prompt，复用 4.2 race + 4.3 sweep 工具跑一遍。
- 产出：**three-number report** — acceptance rate、task correctness、domain coverage（旧 proposal 的三件套复活为作业 rubric）。可提交 LosslessBench 当社区贡献。
- 收尾问题保留旧版那句：if the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?

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
