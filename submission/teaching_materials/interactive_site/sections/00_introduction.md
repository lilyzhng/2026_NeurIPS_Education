<div id="intro" class="section">

## Introduction

</div>

<div id="whymatters" class="section">

### Why it matters

**Every LLM you use generates one token at a time.** This is <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-autoregressive-decoding">autoregressive decoding<span class="glossary-tooltip" id="glossary-autoregressive-decoding" role="tooltip">Generating text one token at a time, with each token depending on the one before it.</span></button>, which is a major bottleneck of inference: producing n tokens takes n passes through a model with tens of billions of parameters. <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-speculative-decoding">Speculative decoding<span class="glossary-tooltip" id="glossary-speculative-decoding" role="tooltip">A generation method that uses a fast smaller draft model to propose several tokens, which are then verified by a larger slower target model.</span></button>, introduced in 2023 ([Leviathan et al., 2023](https://arxiv.org/abs/2211.17192)), is an approach to accelerate this: a lightweight <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-draft-model">draft model<span class="glossary-tooltip" id="glossary-draft-model" role="tooltip">A cheaper model or draft layer that proposes several likely next tokens.</span></button> proposes the next few tokens, and the full <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-target-model">target model<span class="glossary-tooltip" id="glossary-target-model" role="tooltip">The larger model whose output distribution we want to preserve.</span></button> verifies these drafts, accepting or rejecting each one. The verified output has the same <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-probability-distribution">probability distribution<span class="glossary-tooltip" id="glossary-probability-distribution" role="tooltip">The model’s probabilities over all possible next tokens.</span></button> as the target model ([Chen et al., 2023](https://arxiv.org/abs/2302.01318)), which is why speculative decoding is <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-lossless">lossless<span class="glossary-tooltip" id="glossary-lossless" role="tooltip">Produces the same distribution of outputs as the unaccelerated version.</span></button> in theory.

<figure class="wide">
<iframe src="../figures/figure1_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of vanilla and speculative decoding"></iframe>
</figure>
<figcaption><strong>Figure 1.</strong> Vanilla decoding emits one token per target-model pass. Speculative decoding lets a draft model propose a short block, then verifies it with the target model.</figcaption>

**Why is it faster than the vanilla model decoding?** With speculative decoding, a small draft model guesses the next γ tokens (typically 3 to 8), and the target model checks all γ of them in a single <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-forward-pass">forward pass<span class="glossary-tooltip" id="glossary-forward-pass" role="tooltip">Running the model on its current input to produce scores for possible next tokens.</span></button>, which costs about the same as decoding one token. Speed comes from both sides: better drafts get accepted more often, and smarter verification wastes less compute on bad drafts.

**Today, speculative decoding runs under nearly every hosted LLM**, so the speed and quality of decoding affect everyone. Frontier labs lean on it in production: OpenAI cut GPT-5.6 Luna prices by 80% in 2026 and credited the cut partly to a redesigned draft model ([OpenAI, 2026](https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484)), Anthropic's fast mode serves the same Claude Opus model up to 2.5x faster at a premium rate ([Anthropic, 2026](https://platform.claude.com/docs/en/build-with-claude/fast-mode)), DeepSeek ships DSpark in its serving engine for a 51% throughput gain ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)), and Kimi K3 ships with its own draft model ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)). It is a cornerstone topic to learn in the LLM stack.

**The target audience:** If you know that an LLM generates text one token at a time, you have all the prerequisites for this teaching material. The content is designed progressively, each section building on the previous one:

1. <u>How it evolved.</u> How does speculative decoding work, why is it lossless in theory, and how did four generations of draft models build upon each other?
2. <u>When it stays lossless.</u> Introducing [Losslessbench](https://huggingface.co/datasets/lilyzhng/lossless_bench), and a hands-on lab to run the models yourself.
3. <u>What's next?</u> What are the exciting new directions in accelerated inference?

By the end, you will have walked through how speculative decoding evolved and how to serve and evaluate spec models, grounded in research from NeurIPS and ICML: blockwise parallel decoding at NeurIPS 2018 ([Stern et al.](https://arxiv.org/abs/1811.03115)), lossless speculative decoding at ICML 2023 ([Leviathan et al.](https://arxiv.org/abs/2211.17192)), EAGLE-3 at NeurIPS 2025 ([Li et al.](https://arxiv.org/abs/2503.01840)), DFlash at ICML 2026 ([Chen et al.](https://arxiv.org/abs/2602.06036)), and its successor DFlash 2 ([Inco AI, 2026](https://inco.ai/blog/dflash2/)).

You can find the full glossary for reference in [A.1](#glossary).

</div>

<div id="howworks" class="section">

### How it works

To give you a quick example: serving Qwen3-8B on one B200, SGLang, the vanilla model decodes about 230 tokens per second; the first Harry Potter novel is roughly 100,000 tokens, more than seven minutes of decoding. With a DFlash draft model, conversational text decodes about 2.75x faster ([Chen et al., 2026](https://arxiv.org/abs/2602.06036)), ~630 tokens per second, cutting it under 3 minutes. See the Figure 1 comparison.

How much faster exactly, and how do we measure it? Table 1 defines the six metrics. Three of them are deciding factors: drafting time, verification time, and acceptance length. The other three, decoding speedup, per-token latency, and tokens per second, are computed from these three factors.

<div class="table-wrap">
<table>
<thead>
<tr><th>Metric</th><th>Definition</th><th>Determined by</th></tr>
</thead>
<tbody>
<tr><td>Decoding speedup (η)</td><td>η = L_target / L, relative speed over the autoregressive baseline</td><td>Per-token latency L and the baseline latency L_target</td></tr>
<tr><td>Per-token latency (L)</td><td>L = (T_draft + T_verify) / τ, the absolute time per generated token</td><td>T_draft, T_verify, and acceptance length τ</td></tr>
<tr><td>T_draft</td><td>The time the draft model spends proposing tokens</td><td>The draft model's size plus how many draft tokens are needed: the smaller it is, the faster it drafts</td></tr>
<tr><td>T_verify</td><td>The time the target model spends checking the proposed tokens</td><td>The target model's size, and how many draft tokens are verified</td></tr>
<tr><td>Tokens per second</td><td>≈ 1 / L, the throughput the user feels</td><td>Per-token latency L</td></tr>
<tr><td>Acceptance length (τ)</td><td>The average number of draft tokens accepted per verification pass</td><td>How well the draft imitates the target: the closer its guesses, the more tokens survive verification</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 1.</strong> The metrics of speculative decoding. How speed is reported, and three deciding factors (T_draft, T_verify, acceptance length τ).</figcaption>

Below is a math walk-through of achieving 2.3x decoding speedup.

<div class="sptc-py" data-lang="text"><pre>
T_verify = 4.3 ms   # one target forward pass (Qwen3-8B at 230 tok/s ≈ 4.3 ms/token)
T_draft  = 1.3 ms   # drafting cost
τ        = 3 tokens # accepted per verification pass
&nbsp;
L = (1.3 ms + 4.3 ms) / 3 ≈ 1.9 ms per token    # per-token latency
η = 4.3 ms / 1.9 ms ≈ 2.3x                      # speedup: 2.3x
</pre></div>

So far we have covered why speculative decoding is fast. But why is it lossless? The answer is verification via <button class="glossary-term" type="button" aria-expanded="false" aria-describedby="glossary-rejection-sampling">rejection sampling<span class="glossary-tooltip" id="glossary-rejection-sampling" role="tooltip">A method that accepts or replaces draft tokens so the final outputs still follow the target model’s distribution.</span></button>: the target model checks every draft token against its own probabilities and accepts or rejects each one. The beauty of rejection sampling is that losslessness does not depend on the draft: even with a weak draft model, the output still follows the target model's own distribution ([Leviathan et al. 2023](https://arxiv.org/abs/2211.17192), Appendix A.1). Here is how it works in pseudocode:

<div class="sptc-py" data-lang="python"><pre>
# p(x): target model's probability for token x
# q(x): draft model's probability for token x
&nbsp;
for each draft token x:
    accept x with probability
        min(1, p(x) / q(x))
    # q(x) &lt;= p(x): always accepted
    # q(x) &gt;  p(x): accepted with probability p(x)/q(x)
&nbsp;
on the first rejection:
    discard the remaining draft tokens
    resample one token from the residual
        p′(x) = norm( max(0, p(x) - q(x)) )
</pre></div>

Statistically, a token can be emitted in two ways: accepted directly from the draft, which is the accepted mass, or resampled by the target after a rejection, which is the residual mass. The two add up to the same as the target's probability:

<div class="sptc-py" data-lang="text"><pre>
P(x is emitted) = q(x) * min(1, p(x)/q(x))   # accepted mass = min(p(x), q(x))
                + P(reject) * p′(x)          # residual mass = max(0, p(x) - q(x))
                = min(p(x), q(x)) + max(0, p(x) - q(x))
                = p(x)                       # same as the target's probability
</pre></div>

From the 2023 paper (Leviathan et al., Theorem 3.5), the acceptance rate is one minus the total variation distance between the draft and target distributions:

```text
α = 1 − E[D_LK(p, q)]
```

where p and q are the target and draft next-token distributions, and D_LK is the total variation distance between them. The same analysis also derives the acceptance length τ defined in Table 1 from the acceptance rate:

```text
τ = (1 − α^(γ+1)) / (1 − α)
```

where γ is the number of draft tokens per verification cycle.

Everything after 2023 inherits this theorem. Later papers do not re-verify losslessness: as long as verification keeps the accept-or-resample rule above, the guarantee holds however weak the draft is. What Theorem 3.5 adds is a way to read the speed numbers. A reported τ gives the acceptance rate α, and α is one minus a distributional distance: read τ, and you are reading how close the draft's distribution sits to the target's. Under strict verification this distance only decides speed. Once the acceptance threshold is relaxed, the distance would affect output quality, which is where Section 2 picks up.

To summarize, speculative decoding speed comes down to three factors: **(1) drafting time, (2) verification time, and (3) acceptance length.** Section 1 walks through the state-of-the-art architectures and how each generation improves these deciding factors.

</div>
