<div id="lossless" class="section">

## 1. What lossless means

What does lossless acceleration mean for an LLM? Serving Qwen3-8B on one B200, SGLang, the vanilla model decodes about 230 tokens per second; the first Harry Potter novel is roughly 100,000 tokens, more than seven minutes of decoding. With a DFlash draft model, conversational text decodes about 2.75x faster ([Chen et al., 2026](https://arxiv.org/abs/2602.06036)), ~630 tokens per second, cutting it under 3 minutes. See the Figure 1 comparison.

<figure class="wide">
<iframe src="../figures/figure1_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of vanilla and speculative decoding"></iframe>
</figure>
<figcaption><strong>Figure 1.</strong> Vanilla decoding emits one token per target-model pass. Speculative decoding lets a draft model propose a short block, then verifies it with the target model. The animation compares the resulting timelines.</figcaption>

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

The above wraps up the measurement of speculative decoding speed. But how is it lossless in theory? How does it work exactly? The answer is the verification step. The target model checks every draft token against its own probabilities and accepts or rejects each one, a rule called rejection sampling. Verifying losslessness is critical, and it was proven exactly once: as long as verification performs exact rejection sampling, the output provably follows the target model's own distribution ([Leviathan et al. 2023](https://arxiv.org/abs/2211.17192), Appendix A.1). Here is how rejection sampling works in pseudocode:

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

This below shows why the output distribution is unchanged with drafting and verification. A token can be emitted in two ways: accepted directly from the draft, which is the accepted mass, or resampled by the target after a rejection, which is the residual mass. The two add up to the same as the target's probability:

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

Everything after 2023 inherits this theorem. Later papers do not re-verify losslessness, and DFlash contains no explicit validation for being lossless. Then how do we know? The papers do report acceptance length. A reported τ gives the acceptance rate α, and by Theorem 3.5, α is a distributional distance. Read τ, and you are reading how far the draft's distribution sits from the target's.

To summarize, speculative decoding speed comes down to three factors: **(1) drafting time, (2) verification time, and (3) acceptance length.** In the following section, we'll go through the state-of-the-art of model architectures and how each model improves these deciding factors.

</div>

<div id="eagle3" class="section">

### 1.1 EAGLE-3 (2025) – longer acceptance length

The 2023 papers use a separate small LLM as the draft. It guesses from scratch, and hosting a second model costs memory. Medusa ([Cai et al., 2024](https://arxiv.org/abs/2401.10774)) replaced it with extra prediction heads on the target; EAGLE ([Li et al., 2024](https://arxiv.org/abs/2401.15077)) replaced the heads with a single decoder layer that reads the target's hidden features and drafts autoregressively. We highlight EAGLE-3 because it is what ships in production.

Earlier EAGLE models do not improve acceptance length with more training data. This is because the draft layer was trained to predict the target's next hidden feature as well as the next token. This training objective forced the model to reproduce the target's exact feature vectors; as a result, the draft spends its capacity copying features instead of guessing token betters.

**EAGLE-3** ([Li et al., 2025](https://arxiv.org/abs/2503.01840)) addresses this with a less-is-more training objective: it drops feature prediction and predicts the token directly, with features fused from low, middle, and high target layers instead of the top layer only. However, this introduces a new problem: at inference, the draft consumes its own outputs, which drift away from the training distribution, and acceptance collapses from the second step on. EAGLE-3 fixes this with training-time test: during training, the draft unrolls several steps and consumes its own outputs, so the distribution it trains on is the distribution it sees at inference.

<figure class="wide">
<iframe src="../figures/figure2_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of vanilla speculative decoding and EAGLE-3"></iframe>
</figure>
<figcaption><strong>Figure 2.</strong> Vanilla speculative decoding uses a separate small LLM that guesses from scratch. EAGLE-3 replaces it with a single draft layer that reuses the target model's hidden features and LM head.</figcaption>

The result is a longer acceptance length in EAGLE-3. It has a speedup of up to 6.5x over vanilla decoding, about 1.4x over EAGLE-2, and it is one of the most widely adopted draft models in production frameworks, with native support in both SGLang and vLLM.

<u>But one bottleneck remains: the draft layer proposes tokens one at a time, so drafting itself is still sequential.</u>

</div>

<div id="dflash" class="section">

### 1.2 DFlash (2026) – shorter drafting time

The key design choice of **DFlash** ([Chen et al., 2026](https://arxiv.org/abs/2602.06036)) is to make drafting parallel: the whole block at once, instead of token by token. The draft is a lightweight block diffusion model: it predicts an entire block of tokens in a single forward pass, conditioned on context features extracted from the target model.

<figure class="wide">
<iframe src="../figures/dflash_draft_chalk.html" style="width:100%;height:560px;border:1px solid var(--line);border-radius:10px;" loading="lazy" title="Animated comparison of EAGLE-3 and DFlash drafting"></iframe>
</figure>
<figcaption><strong>Figure 3.</strong> EAGLE-3 drafts tokens serially, one at a time. DFlash drafts a whole block in parallel, with the target model's context features injected once per block.</figcaption>

As a result, DFlash cuts drafting time. This removes autoregressive drafting as the bottleneck: over 6x lossless acceleration across a range of models and tasks, up to 2.5x higher speedup than EAGLE-3.

<u>However, parallelism introduces its own cost: the block positions are predicted independently, so draft tokens cannot see each other, and acceptance decays toward the end of the block.</u>

</div>

<div id="dspark" class="section">

### 1.3 DeepSeek DSpark (2026) – shorter verification time

Unlike the previous models that optimize the draft mechanism, **DSpark** ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) optimizes the verification mechanism: verify only the draft tokens that are worth it. DSpark keeps the parallel draft backbone and adds two modules.

- A lightweight sequential head restores dependencies inside the block, so later positions can condition on earlier ones.
- A confidence head estimates how likely each draft prefix is to survive verification, and a load-aware scheduler sets the verification length per request, based on the estimated survival probability and the engine's throughput profile.

<figure class="wide">
<iframe src="../figures/figure4_chalk.html" style="width:100%;height:620px;border:1px solid var(--line);border-radius:10px;" loading="lazy" title="Animated comparison of DFlash and DSpark drafting"></iframe>
</figure>
<figcaption><strong>Figure 4.</strong> DSpark adds a sequential head for intra-block dependencies and a confidence head that scores each draft position; a load-aware scheduler trims low-confidence queues before verification.</figcaption>

Consequently, DSpark cuts verification time. Offline, DSpark improves accepted length by 16–31% over state-of-the-art drafters. Deployed in the DeepSeek-V4 production serving stack, it accelerates per-user generation by 60–85% at matched throughput over the MTP-1 production baseline ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)). DeepSeek open-sourced the DSpark checkpoints together with DeepSpec, an open-source training repository for speculative decoding.

<u>DSpark cuts verification time, and keeps DFlash's parallel drafting. What about acceptance length? Positions in the block are still predicted independently, so the decay problem at the end of long blocks still remains.</u>

</div>

<div id="dflash2" class="section">

### 1.4 DFlash 2 (2026) – longer acceptance length

**DFlash 2** ([Inco, 2026](https://inco.ai/blog/dflash2/)) addresses this decay on the draft side, with two additions to the DFlash architecture. A lightweight path selector scores adjacent token pairs and picks a coherent sequence through the top candidates at each position, instead of taking independent top-1 predictions. Two-tap local convolutions in the backbone strengthen dependencies within the block, reducing the accuracy drop toward block ends.

<figure class="wide">
<iframe src="../figures/figure5_chalk.html" style="width:100%;height:620px;border:1px solid var(--line);border-radius:10px;" loading="lazy" title="Animated comparison of independent top-1 selection and DFlash 2 path selection"></iframe>
</figure>
<figcaption><strong>Figure 5.</strong> To keep the block coherent, DFlash 2 adds a path selector that picks coherent token sequences across adjacent positions, and local convolutions that reduce acceptance decay toward the end of the block.</figcaption>

As we can tell, DFlash 2 raises acceptance length. The two additions produce 21% more output per verification pass than DFlash, at 1.3% added latency, and 2.7x to 3.4x throughput over autoregressive decoding on Qwen3.8-27B ([Inco, 2026](https://inco.ai/blog/dflash2/)).

<u>Note that DFlash 2 argues drafting should stay parallel: it replaces DSpark's sequential head with a parallel selector. After going through the evolution of these four architectures, do you have a new speculative decoding idea that could win the next SOTA number?</u>

</div>

<div id="race" class="section">

### 1.5 Case study: the decoding race

With all 5 models introduced, the race can now run in full comparison. See Figure 6. All 5 models decode the same sentence on the same target model.

<figure class="wide">
<iframe src="../figures/figure6_chalk.html" style="width:100%;height:680px;border:1px solid var(--line);border-radius:10px;" loading="lazy" title="Animated comparison of five speculative decoding approaches"></iframe>
</figure>
<figcaption><strong>Figure 6.</strong> The full decoding race.</figcaption>

<div class="table-wrap">
<table>
<thead>
<tr><th>Method</th><th>τ</th><th>Speedup</th><th>Engines</th><th>Official drafters</th></tr>
</thead>
<tbody>
<tr><td>EAGLE-3</td><td><span class="num">2.66</span></td><td>6.5x</td><td>SGLang, vLLM</td><td>Llama, Qwen, DeepSeek V3, Kimi K2.5</td></tr>
<tr><td>DFlash</td><td><span class="num">3.11</span></td><td>&gt;6x</td><td>SGLang, vLLM, TRT-LLM, llama.cpp</td><td>Meta, Poolside, NVIDIA, Xiaomi</td></tr>
<tr><td>DSpark</td><td><span class="num">3.72</span></td><td>60–85% vs MTP-1</td><td>DeepSeek-V4 stack</td><td>GLM-5.2, Kimi K3 (RedHat)</td></tr>
<tr><td>DFlash 2</td><td>(to be measured)</td><td>2.7–3.4x</td><td>SGLang, vLLM, llama.cpp, Ollama</td><td>Qwen3.8-27B, Muse Glimmer</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 2 (mock). The four models at a glance.</strong></figcaption>

All four models are in production today. Since March 2025, EAGLE-3 draft heads ship for Llama, Qwen, and DeepSeek V3. By spring 2026, DFlash was integrated into SGLang, vLLM, TensorRT-LLM, and llama.cpp, and NVIDIA reported up to 15x throughput with it on Blackwell GPUs ([NVIDIA, 2026](https://developer.nvidia.com/blog/boost-inference-performance-up-to-15x-on-nvidia-blackwell-using-dflash-speculative-decoding/)). DFlash alone has been downloaded more than 3.5 million times in seven months. By mid-2026, model builders release official drafters alongside the models themselves: Meta, Poolside, and NVIDIA for DFlash ([Inco, 2026](https://inco.ai/blog/dflash2/)), Red Hat for DSpark ([RedHatAI, 2026](https://huggingface.co/RedHatAI/GLM-5.2-speculator.dspark-preview)), and in July 2026, Kimi K3 shipped with its own speculator, trained during post-training ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)). See Table 2.

So far we have covered what lossless means. In the next section, we will discuss what lossless does not mean.

</div>
