## 框架（定稿骨架，2026-08-27）

**语气总纪律（Round 10）：** 谁主张谁举证。2.1 只放引文和可复核事实（零推断），2.2 只放各家自己的文档原话，2.3 我们自证。全节没有一句"提出问题但不自己回答"。不写"他们没测所以有问题"——真给现有数据集加 grader 大概率测出一模一样，因为那些域正是 lossless 最稳的地方。

**§1 → §2 衔接（开场段，Round 8/9）：**
- Section 1 收在三个 factor（T_draft、T_verify、τ）和 Table 1 的六行指标上。开场指出：六行全是速度家族，没有一行看 token 说了什么。
- 立刻补上原因（不是指控）：这不是疏忽，是定理的兑现——分布相等 by construction，质量不可能变，不可能变的量不需要仪表。整个评估体系把定理当质量保险用。
- 引出本节任务：那这份保险的条款到底写了什么、没写什么。开场句方向："Section 1 ended with three deciding factors. Notice what is not among them: nothing measures the output itself. Given the theorem, nothing needs to. This section reads what the theorem actually covers."

### 2.1 What lossless doesn't mean in the papers

核心逻辑句式（Round 11）：**claim 的范围 = 证据的范围**。论文报的 lossless 是"在测过的域上成立"，读者听成"在所有域上成立"。本小节把范围线描出来，不指控任何人。

段落顺序（Round 12 定稿）：
1. **报数引文 + 各自的测试域**：EAGLE-3 up to 6.5x（[Li et al., 2025](https://arxiv.org/abs/2503.01840)，五任务：MT-Bench、HumanEval、GSM8K、Alpaca、CNN/DM + reasoning models）；DFlash over 6x lossless（[Chen et al., 2026](https://arxiv.org/abs/2602.06036)，math/code/chat）；DSpark 60–85% vs MTP-1（[DeepSeek, 2026](https://arxiv.org/abs/2607.05147)，offline benchmarks + DeepSeek-V4 live traffic）。
2. **验证域清单（show don't tell，Table 位）**：Method × 验证数据集一张表，从各论文实验节 + DeepSpec 九数据集（gsm8k/math500/aime25；humaneval/mbpp/livecodebench；mt-bench/alpaca/arena-hard-v2）抄格。读者自己看出清一色 math/code/chat。
   - TODO：从三篇论文实验节把每格核对抄出。
3. **lossless 是硬术语的引文**（词有准入条件，field 自己在执法）：
   - EAGLE-3 Table 1 caption 原文："Methods like Medusa relax acceptance conditions under non-greedy settings, which do not guarantee lossless acceleration. Therefore, we do not compare EAGLE-3 with these methods when temperature=1."
   - DFlash 评 TiDAR："...though final generation quality is not yet lossless."
4. **OpenRouter 流量对照**：真实流量里 roleplay、creative writing、marketing、translation、agentic workflows 占大头（[openrouter.ai/rankings](https://openrouter.ai/rankings)）。清单里 verified 的域只覆盖流量的 X%。
   - TODO（必须真算，不能拍脑袋）：拉 OpenRouter rankings category 份额，{programming/math/chat} 归 verified，算出实际占比。顺手做小图：份额条形图，verified 部分涂色。
5. **落锤句**："Measured on math and code does not mean lossless across every domain. It doesn't mean it's lossless on the rest of the X%." 这时是读者已自己得出的结论，我们只是说出来。
6. **no-grader 事实，中性陈述收窄**（8/31 从 2.1 正文删除，若 2.2 放不下就弃用；也可作 2.3 动机）：DeepSpec eval.py 只记四个 acceptance 指标，全库无 grader/pass@1/accuracy；GSM8K 在此是流量样本不是数学考试。紧跟让步句（Round 10）："On the domains the harness covers, grading the outputs would likely show no difference; these are the domains where the draft guesses best."
7. **Teaser 钓向 2.3**：acceptance 本身 domain-conditional（DSpark 原文："structured requests like code naturally sustain higher acceptance rates than open-ended chat"；§1 hook 已埋种子：对话域 2.75x vs 数学域 6.08x）。"Whether the same holds on domains that are harder to verify is an empirical question. Section 2.3 measures it."
8. **定理小字（一句带过）**：保证是 distribution-level 不是 sequence-level——同 prompt 两次输出可以不同，保证的是分布。

### 2.2 Lossless in deployment

衔接句（Round 8）：三代各压一个 factor（1.1 τ、1.2 T_draft、1.3 T_verify），压到 DSpark 优化 T_verify 这一步，优化本身开始蹭到定理的前提。§1 的英雄在这里是边界最紧的地方。

素材（全部是各家自己的文字，按"离定理越来越远"排）：
1. **DSpark Appendix A 反例**（自己差点打破；2.1 只留条件本身，故事放这里。注意他们修好了，所以只能说边界真实到要写附录防它，不能说漏了）："Lossless speculative decoding strictly requires the non-anticipating property: admission decisions must not depend on future candidate tokens... A retrospective global search would thus inadvertently leak x into the admission decision... introducing selection bias (we provide a concrete counterexample demonstrating this theoretical violation in Appendix A)." 修复靠 early-stopping "ensuring exact target-distribution recovery"。教学点：保证有前提，前提会被一个工程细节悄悄打破，DeepSeek 自己专门写附录防它。
2. **DSpark §5.2**（理论到生产有缝）："directly deploying this algorithm into a production environment exposes two fundamental conflicts with real-world infrastructure."（smooth capacity curve 假设 vs 真实 jagged SPS；动态 token 调度 vs CUDA graph replay/ZOS）
3. **vLLM typical-acceptance**：官方文档自己描述为拿质量换速度（[vLLM docs](https://docs.vllm.ai/en/latest/features/spec_decode.html)）。
4. **DeepSpec `--confidence-threshold` 旋钮**：超阈值即免验直收。lossless-for-speed 的交易浓缩在一个官方 flag 里。
5. **生产 stack 的 lossy/lossless 分类**（§1 Round 72 挪来的素材，三连句式复活）：quantized weights lossy、KV-cache compression lossy、speculative decoding——Lossless，但仅指 exact verification 那一步。定理盖一步，生产 stack 比一步长（fp4 + kv routing + pd disagg + relaxed acceptance 全在证明假设之外）。

### 2.3 Introducing Lossless Bench

<!-- 2.3 开场备选（8/31）：Theoretical losslessness (Section 1) and algorithmic losslessness (Section 2.2) are covered; this section measures output stability, the layer no engine guarantees. 不提"借鉴 vLLM"，我们有自己的思路。 -->

1. **设计动机直接回answer 2.1 的清单**：五个域照着清单的空白处选——coding、agent workflows（verified 侧）+ creative writing、guardrails、frontend design（空白侧）。同一 model、reference vs accelerated 两套部署、判 behavior 不判 token overlap（[LosslessBench](https://lilyzh.ng/writing/losslessbench/)）。
2. **先报确认，再报例外（Round 10 举证纪律）**：五个域里四个无显著差异；owner-shipped 加速（Kimi K3）0.3 分。我们的测量大部分在确认 lossless。
3. **例外是域局部的**：vendor 组装 stack（fp4 + spec dec + kv routing + pd disagg，定理条件外）× 难验证域（frontend design）= 5.6 分（76.9 → 71.2）。日历图（Figure：id673_fp8 vs id673_fp4，要求的 translucent popup 整个消失）。失败是 qualitative 不是 cosmetic。
4. **Sweep 实验（original result 图）**：`--confidence-threshold` 从紧到松扫一遍，acceptance 爬升、task accuracy 下降，两数反向走。题句用原句："Acceptance rate is not accuracy."
   - TODO：跑 sweep，画 trade-off 曲线（acceptance rate vs task accuracy）。这是全文核心原创图。
5. **Scope statement 收尾（两句，不单开小节）**：所有数字 batch size 1 / 低并发，高并发下引擎可能直接关 spec dec；连 speed 都是 deployment-conditional 的（Alex Zhang [spec-ptc](https://alexzhang13.github.io/blog/2026/spec-ptc/)："it's very difficult to estimate the exact speed-ups because it's highly dependent on... the load of your serving engine, and the actual choices the harness makes"）。结论句方向：lossless 在被验证过的地方成立；我们把验证扩到没人验证的地方，发现一个域局部的例外。

### TODO 汇总
- [ ] Table：验证域清单，从 EAGLE-3/DFlash/DSpark 实验节逐格核对抄出
- [ ] 算 OpenRouter verified 流量占比 + 份额条形图（verified 涂色）
- [ ] 跑 confidence-threshold sweep，画 acceptance vs accuracy 曲线（核心原创图）
- [ ] 日历对比图已有（id673_fp8/fp4），迁入 2.3
- [ ] 开场段落草稿（§1 三 factor 衔接）
- [ ] **重做 LosslessBench 归因实验（最重要）**：现有 5.6 分 frontend gap 是 vendor 全家桶 stack（fp4 quant + spec dec + kv routing + pd disagg）测出来的，degradation 无法归因到 speculative decoding——很可能是 quantization 造成的。需要隔离实验：同一模型、只开/关 spec decoding（其他配置全部固定），在 frontend 域重测，证明 spec decoding 本身在 frontend 上有损。需要选定一个能这样部署的模型
- [ ] 2.3 结尾补 ending + 递给 Section 3 的 transition line（等 sweep/归因实验结果一起定稿）
- [ ] sweep 出结果后：把 quality-aware draft training 段（引用见 03 文件 git 历史：DistillSpec/EAGLE/LK losses/Judge Decoding）改写成"操作结论"形态接在 sweep 图后——答案=保质量就保持严格 threshold（SGLang 默认 1.0），verifier 侧 Judge Decoding 是唯一折中，draft 侧无工具；不写成 unanswered limitation

<figure>
<div class="fig2">
<img src="https://lilyzh.ng/writing/losslessbench/id673_fp8.png" alt="reference render of the calendar prompt, with the requested translucent popup implemented" /> <img src="https://lilyzh.ng/writing/losslessbench/id673_fp4.png" alt="accelerated render of the same prompt, a clean page with the calendar popup missing" />
