<div id="intro" class="section">

## Introduction

**Every LLM you use generates one token at a time.** This is autoregressive decoding, which is a major bottleneck of inference: producing n tokens takes n passes through a model with tens of billions of parameters. Speculative decoding, introduced in 2023 ([Leviathan et al., 2023](https://arxiv.org/abs/2211.17192)), is an approach to accelerate this: a lightweight draft model proposes the next few tokens, and the full target model verifies these drafts, accepting or rejecting each one. The verified output has the same distribution as the target model ([Chen et al., 2023](https://arxiv.org/abs/2302.01318)), which is why speculative decoding is lossless in theory.

**Why is it faster than the vanilla model decoding?** With speculative decoding, a small draft model guesses the next γ tokens (typically 3 to 8), and the target model checks all γ of them in a single forward pass, which costs about the same as decoding one token. Speed comes from both sides: better drafts get accepted more often, and smarter verification wastes less compute on bad drafts.

**Today, speculative decoding runs under nearly every hosted LLM**, so the speed and quality of decoding affect everyone. Frontier labs lean on it in production: OpenAI cut GPT-5.6 Luna prices by 80% in 2026 and credited the cut partly to a redesigned draft model ([OpenAI, 2026](https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484)), Anthropic's fast mode serves the same Claude Opus model up to 2.5x faster at a premium rate ([Anthropic, 2026](https://platform.claude.com/docs/en/build-with-claude/fast-mode)), DeepSeek ships DSpark in its serving engine for a 51% throughput gain ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)), and Kimi K3 ships with its own draft model ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)). It is a cornerstone topic to learn in the LLM stack.

If you know that an LLM generates text one token at a time, you have all the prerequisites for this article.

In this teaching material, we have designed content progressively. Each section builds on the previous one:

1. <u>What lossless means.</u> How does speculative decoding work? Why is it lossless in theory?
2. <u>What it doesn't mean.</u> Introducing [Losslessbench](https://huggingface.co/datasets/lilyzhng/lossless_bench) to test beyond the math and coding domains, with a hands-on lab to reproduce every number yourself.
3. <u>What's next?</u> What are the exciting new directions in accelerated inference?

</div>
