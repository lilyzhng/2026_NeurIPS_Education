# Graphics notes — interactive site

整理日期 2026-09-04。两部分：现有 graphics 清单 + Modal LLM Engineer's Almanac 可借鉴的图形模式。

## A. 现有 graphics 清单

| Figure | 文件 | 所在 section | 内容 | 状态 |
|---|---|---|---|---|
| Fig 1 | figures/figure1_chalk.html | 00 intro | vanilla vs speculative decoding 动画 | ✅ 模板（其余 figure 按它改：小 20%、dark forest 底、橡皮擦 replay 按钮） |
| Fig 2 | figures/figure2_chalk.html | 1.1 EAGLE-3 | vanilla spec dec vs EAGLE-3 draft layer | 🔴 fuse 后 Veo 3 block 有 disjoint 部分 |
| Fig 3 | figures/dflash_diffusion_analogy_chalk-v5.html | 1.2 DFlash | 袋鼠两 lane：serial paint vs parallel denoise（Twemoji 🦘 alpha 描边 32×32），结尾 "What about drafting in parallel?" | ✅ 已嵌入（2026-09-04） |
| Fig 4 | figures/dflash_flat_cost_chalk-v1.html | 1.2 DFlash | flat-cost 交互图：drafting cost vs γ，滑块 + break-even 标注 | ✅ 已嵌入（2026-09-04） |
| Fig 5 | figures/dflash_draft_chalk.html | 1.2 DFlash | EAGLE-3 串行 drafting vs DFlash 整块去噪 + context KV 注入 | — |
| Fig 6 | figures/figure4_chalk.html | 1.3 DSpark | sequential head + confidence head + load-aware scheduler | — |
| Fig 7 | figures/figure5_chalk.html | 1.4 DFlash 2 | 独立 top-1 vs path selector | 🔴 需要修 |
| Fig 8 | figures/figure6_chalk.html | 1.5 race | 五模型 decoding race（H100 实测 + Inco 报告值） | — |
| Fig 9 | figures/figure7_chalk.html | 02 lossless | rejection sampling vs relaxed acceptance（猫狗例子） | 🔴 手机视图拉伸 |
| Fig 10 | figures/figure8_chalk.html | 02 lossless | peeking scheduler 的 selection bias | — |
| Fig 11 | figures/figure9_chalk.html | 02 lossless | OpenRouter traffic 按任务类型，83% 未被测过 | — |
| Fig 12–15 | fig10/11 png + demo/*.html | 02 lossless | LosslessBench 结果、threshold sweep、race demo | — |
| Fig 16 | fig13_runs_h100.svg | 02 lossless | Qwen3-8B H100 decode throughput bar chart | — |
| Fig 17 | demo/knob_pages/ | 02 lossless | SGLang acceptance threshold knob | — |
| Fig A2 | figures/figureA2_chalk.html | 05 appendix | — | — |
| 附录 | fig14_ownership_migration.svg | 05 appendix | acceleration 工作从 serving layer 迁移到 labs 的时间线 | — |

## B. Modal Almanac 可借鉴的图形模式

来源：[LLM Engineer's Almanac](https://modal.com/llm-almanac/advisor)（Charles Frye @ Modal）。

1. **Mad-libs 句式控件** — Advisor 把参数写成填空句："I want to serve ___ with ___…"。参数读起来像意图，适合混合受众。
2. **点结果 → 可复制的代码** — 图上每条线对应一段可运行的 config（版本、CLI args、GPU），带 Copy 按钮。figure 变成可复现 artifact。
3. **轴旁注 "← Lower is better"** — 几乎零成本，可读性大。
4. **"Poke holes in our results" FAQ** — 主动交代 dataset、版本、上限/下限口径、150ms 客户端开销。预先拆掉审稿人式质疑。
5. **骰子 "I'm feeling curious"** — 随机一个 config，邀请探索。
6. **Image-as-tensor**（block-quants 页）— 用真实图片的 posterization 让 block 结构"看得见"。借类比教学。
7. **Bit-pattern explorer**（quant-formats 页）— 点任意一个 float → 展开 sign/exponent/significand、hex、base-2/10 求值。微观可点击探索。
8. **Token timing replay**（token-timing-simulator 页）— 双栏逐 token 流式回放实测延迟（DFlash ON vs OFF）。是"真实录制回放"，不是合成动画。
9. **γ\* roofline 计算器**（spec-dec-roofline 页）— speedup vs draft length 曲线 + 直接算出最优 γ\* 写进 legend；双配置对比；"By draft length / At optimal" 切换；诚实声明 "It is only a model!" + 署名推导来源（Fergus Finn / Doubleword）。

注意：Modal 已有 spec-dec roofline + DFlash demo，我们网站的差异化在教学法（chalkboard、lossless 直觉、threshold sweep 到 lossy 区域），可做外链 "keep exploring"。

## C. Section 1.2（DFlash）图形提案

现状：Figure 3 动画（EAGLE-3 串行 vs DFlash 整块去噪）。正文还有两个论点只有文字没有图。

1. **Flat-cost vs linear-cost 小图（首选，借 B9）** — x = block size γ，y = drafting time：EAGLE-3 线性上升（γ passes），DFlash 水平线（1 pass）。γ 滑块交互。标注 "DFlash 5 层仍快于 EAGLE-3 单 层"。这是 1.2 的核心定量主张，目前完全没有图。和 Modal roofline 页不撞车：他们画端到端 speedup，我们画 drafting cost 随 block 的缩放。
2. **图像去噪类比 panel（借 B6）** — 正文用了 diffusion 类比但 Figure 3 只有 token block。左栏放真实图片从噪声并行去噪 vs 逐角绘制，右栏对应 MASK 行 → token。让 "borrowed from diffusion" 一眼成立。
3. **KV 注入小示意图** — benefit 2（target 每个 prefix 位置的 feature 转成 KV 注入每个 draft layer）目前纯文字。一张静态 chalk 小图即可。
4. **Drafting-time mini race（借 B8，可选）** — 回放实测 drafting 延迟：EAGLE-3 打 8 拍 vs DFlash 1 拍。可做进 Figure 3 的计时条，注意别和 1.5 的 Figure 6 race 重复。
5. **MASK 位置 explorer（借 B7，建议留给 1.4）** — 点击 MASK 位置看 top-k candidate list。候选 list / recall 数字本来就在 1.4，放那边更贴。
