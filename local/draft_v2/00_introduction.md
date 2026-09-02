# 0. Introduction

## 定稿（synced from Desktop v4, 2026-09-01）

What is speculative decoding? Introduced in 2023, speculative decoding decouples draft generation from target verification ([Leviathan et al., 2023](https://arxiv.org/abs/2211.17192)): a draft mechanism proposes tokens, and a verification mechanism accepts or rejects them. The verified output has the same distribution as the target model ([Chen et al., 2023](https://arxiv.org/abs/2302.01318)), which is why speculative decoding is lossless.

Why is it faster than the vanilla model decoding ? The vanilla LLM is autoregressive: it decodes one token at a time. To produce n tokens, the original model runs n forward passes. With speculative decoding, a small draft model guesses the next γ tokens (typically 3 to 8), and the target model checks all γ of them in a single forward pass, which costs about the same as decoding one token. Speed comes from both sides: better drafts get accepted more often, and smarter verification wastes less compute on bad drafts. 

Today, speculative decoding runs under nearly every hosted LLM, and agent workflows chain dozens of model calls per task, so the cost of decoding is paid many times over. Frontier labs lean on it in production: OpenAI cut GPT-5.6 Luna prices by 80% in 2026 and credited the cut partly to a redesigned draft model ([OpenAI, 2026](https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484)), Anthropic's fast mode serves the same Claude Opus model up to 2.5x faster at a premium rate ([Anthropic, 2026](https://platform.claude.com/docs/en/build-with-claude/fast-mode)), DeepSeek ships DSpark in its serving engine for a 51% throughput gain ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)), and Kimi K3 ships with its own draft model ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)). It is a cornerstone topic to learn in the LLM stack.

In this teaching material, we have designed content progressively. Each section builds on the previous one:

1. What lossless means. How does speculative decoding work? Why is it lossless in theory?  
2. What it doesn't mean. Does lossless inference hold true beyond the math and coding domains?  
3. What's next? What are the exciting new directions in accelerated inference?  
4. How to train, serve, and test it. Run a speculative decoding model with SGLang.

## References

1. Smith, J. E. (1981). A Study of Branch Prediction Strategies. ISCA 1981. https://dl.acm.org/doi/10.5555/800052.801871
2. Stern, M., Shazeer, N., & Uszkoreit, J. (2018). Blockwise Parallel Decoding for Deep Autoregressive Models. NeurIPS 2018. https://arxiv.org/abs/1811.03115
3. Leviathan, Y., Kalman, M., & Matias, Y. (2023). Fast Inference from Transformers via Speculative Decoding. ICML 2023. https://arxiv.org/abs/2211.17192
4. Chen, C., Borgeaud, S., Irving, G., Lespiau, J.-B., Sifre, L., & Jumper, J. (2023). Accelerating Large Language Model Decoding with Speculative Sampling. https://arxiv.org/abs/2302.01318
5. OpenAI (2026). Announcing a Major Price Drop for 5.6 Terra and Luna and Fast Mode for 5.6-Sol. https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484
6. Anthropic (2026). Fast Mode (Research Preview). Claude Platform Docs. https://platform.claude.com/docs/en/build-with-claude/fast-mode
7. DeepSeek (2026). DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation. https://arxiv.org/abs/2607.05147
8. Kimi Team (2026). Kimi K3 Technical Report. https://arxiv.org/abs/2607.24653
