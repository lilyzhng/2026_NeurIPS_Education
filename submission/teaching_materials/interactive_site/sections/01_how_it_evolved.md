<div id="lossless" class="section">

## 1. How speculative decoding evolved

Speculative decoding speed comes down to three factors: **drafting time, verification time, and acceptance length**. Four generations of speculative decoding models each remove one bottleneck: EAGLE-3 lengthens acceptance, DFlash cuts drafting time, DSpark cuts verification time, and DFlash 2 pushes acceptance further. We walk through them in order.

</div>

<div id="eagle3" class="section">

### 1.1 EAGLE-3 (NeurIPS 2025) – longer acceptance length

The 2023 papers use a separate small LLM as the draft. It guesses from scratch, and hosting a second model costs memory. Medusa ([Cai et al., 2024](https://arxiv.org/abs/2401.10774)) replaced it with extra prediction heads on the target; EAGLE ([Li et al., 2024](https://arxiv.org/abs/2401.15077)) replaced the heads with a single decoder layer that reads the target's hidden features and drafts autoregressively (Figure 3). We highlight EAGLE-3 because it is what ships in production.

Earlier EAGLE models do not improve acceptance length with more training data. This is because the draft layer was trained to predict the target's next hidden feature as well as the next token. This training objective forced the model to reproduce the target's feature vectors; as a result, the draft spends its capacity copying features instead of guessing tokens better.

**EAGLE-3** ([Li et al., 2025](https://arxiv.org/abs/2503.01840)) addresses this with a less-is-more training objective: it drops feature prediction and predicts the token directly, with features fused from low, middle, and high target layers instead of the top layer only. However, this introduces a new problem: at inference, the draft consumes its own outputs, which drift away from the training distribution, and acceptance collapses from the second step on. EAGLE-3 fixes this with training-time test: during training, the draft unrolls several steps and consumes its own outputs, so the distribution it trains on is the distribution it sees at inference.

<figure class="wide">
<iframe src="../figures/figure2_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of vanilla speculative decoding and EAGLE-3"></iframe>
</figure>
<figcaption><strong>Figure 3.</strong> Vanilla speculative decoding uses a separate small LLM that guesses from scratch. EAGLE-3 replaces it with a single draft layer that reuses the target model's hidden features and LM head.</figcaption>

The result is a longer acceptance length in EAGLE-3. It reaches a speedup of up to 6.5x over vanilla decoding on HumanEval, about 1.4x over EAGLE-2, and it is one of the most widely adopted draft models in production frameworks, with native support in both SGLang and vLLM.

<p class="pullquote">One bottleneck remains. A small draft model runs fast, but it still proposes one token at a time. Can drafting be parallel instead?</p>

</div>

<div id="dflash" class="section">

### 1.2 DFlash (ICML 2026) – shorter drafting time

The key design choice of **DFlash** ([Chen et al., 2026](https://arxiv.org/abs/2602.06036)) is to make drafting parallel: generate the whole block at once, instead of token by token (Figure 4).

The beauty of DFlash is this very smart idea of diffusion block drafting. DFlash borrows it from diffusion models. In image and video generation, a diffusion model starts from pure noise and denoises every pixel in parallel, refining the whole canvas at once instead of painting it pixel by pixel (see the teaser figure). Text diffusion models carry the same idea over ([Arriola et al., 2025](https://arxiv.org/abs/2503.09573)): replace the noise with MASK tokens, and let the model predict every masked position in parallel. DFlash applies this to drafting: the draft block starts as a row of MASK tokens.

<figure class="wide">
<iframe src="../figures/dflash_draft_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of EAGLE-3 and DFlash drafting"></iframe>
</figure>
<figcaption><strong>Figure 4.</strong> Diffusion denoises every position in parallel, and DFlash carries that into drafting: EAGLE-3 drafts tokens sequentially, one at a time, while DFlash denoises a whole block of MASK tokens in one pass, with the target model's context features injected once per block. Timing follows the paper's numbers: one pass of DFlash's 5-layer draft costs about five 1-layer EAGLE-3 steps &mdash; slower than a single EAGLE-3 step &mdash; but it drafts a block of 16 tokens at once, while EAGLE-3 drafts 8 tokens in 8 steps.</figcaption>


Diffusion drafting brings two benefits.

- **Generating the whole block in a single forward pass makes drafting fast.** An autoregressive draft spends one forward pass per token, so drafting γ tokens costs γ passes. DFlash drafts all γ positions in one pass, and the cost stays flat as the block grows (Figure 5). The flat cost also buys capacity: EAGLE-3 keeps a single layer to stay fast, while DFlash can afford five layers and still drafts faster. Five layers generating 16 tokens beat EAGLE-3's single layer generating 8, on both drafting cost and acceptance length.
- **Conditioning on the target model's context features makes the drafts accurate.** Feeding the draft only the last token's fused feature has two problems: it carries a single position, and a signal added only at the bottom of the stack fades in deeper layers. DFlash instead converts the target's features for every verified prefix position into keys and values and injects them into each draft layer's KV cache (Figure 6), so every layer sees the full context while the block is filled in. The result is high-quality drafts with higher acceptance rates.

<figure class="wide">
<iframe src="../figures/dflash_flat_cost_chalk-v1.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Interactive chart of drafting cost versus block size for EAGLE-3 and DFlash"></iframe>
</figure>
<figcaption><strong>Figure 5.</strong> Drafting cost versus block size. EAGLE-3 keeps one layer to stay fast, so drafting &gamma; tokens costs &gamma; passes; DFlash spends five layers in one pass, flat at any &gamma;.</figcaption>

<figure class="wide">
<iframe src="../figures/dflash_kv_injection_chalk-v1.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Diagram of DFlash injecting target model context features as keys and values into every draft layer"></iframe>
</figure>
<figcaption><strong>Figure 6.</strong> DFlash converts the target's features at every verified prefix position into keys and values, injected into each draft layer's KV cache, so every layer sees the full prefix. EAGLE-3 conditions on the last token only, at the bottom layer only.</figcaption>

As a result, DFlash cuts drafting time. This removes autoregressive drafting as the bottleneck: over 6x lossless acceleration across a range of models and tasks, up to 2.5x higher speedup than EAGLE-3.

<p class="pullquote">The block positions are predicted independently, so draft tokens cannot see each other. How do we handle the acceptance decay toward the end of the block?</p>

</div>

<div id="dspark" class="section">

### 1.3 DeepSeek DSpark (2026) – shorter verification time

Unlike the previous models that optimize the draft mechanism, **DSpark** ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) optimizes the verification mechanism: verify only the draft tokens that are worth it. DSpark keeps the parallel draft backbone and adds two modules (Figure 7).

- A lightweight sequential head restores dependencies inside the block, so later positions can condition on earlier ones.
- A confidence head estimates how likely each draft prefix is to survive verification, and a load-aware scheduler sets the verification length per request, based on the estimated survival probability and the engine's throughput profile.

<figure class="wide">
<iframe src="../figures/figure4_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of DFlash and DSpark drafting"></iframe>
</figure>
<figcaption><strong>Figure 7.</strong> DSpark adds a sequential head for intra-block dependencies and a confidence head that scores each draft position; a load-aware scheduler trims low-confidence queues before verification.</figcaption>

Consequently, DSpark cuts verification time. Offline, DSpark improves accepted length by 16–31% over state-of-the-art drafters. Deployed in the DeepSeek-V4 production serving stack, it accelerates per-user generation by 60–85% at matched throughput over the MTP-1 production baseline ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)). DeepSeek open-sourced the DSpark checkpoints together with DeepSpec, an open-source training repository for speculative decoding.

<p class="pullquote">DSpark cuts verification time, and its sequential head eases the decay. But that head walks token by token again. Was giving up parallel drafting the right trade?</p>

</div>

<div id="dflash2" class="section">

### 1.4 DFlash 2 (2026) – longer acceptance length

DSpark tries to address the acceptance decay with a sequential token head, but **DFlash 2** ([Inco, 2026](https://inco.ai/blog/dflash2/)) argues drafting should stay parallel: it replaces DSpark's sequential head with a parallel selector. The cost gap is the argument: the sequential head re-predicts a full vocabulary distribution at every position, 77.8M parameters and 9.6% latency, while the selector does its job with 2.0M and 0.6%.

What makes parallel selection possible is that the right tokens are usually already there. Take a verified prefix "The fastest way to" and four masked positions. Each position's short candidate list contains the token the target would pick, but taking the top candidate at every position independently yields "get to to school": two neighbors picked the same word, and the sentence breaks. The coherent "get to school quickly" was sitting in the lists all along. Inco measured how much this is worth: if a perfect judge always picked the right candidate out of the top 16, acceptance length would jump from 4.27 to 6.79. The missing tokens are rarely the problem; the missing judgment is. The job is selection, and selection can run in parallel (Figure 8).

<figure class="wide">
<iframe src="../figures/figure5_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of independent top-1 selection and DFlash 2 path selection"></iframe>
</figure>
<figcaption><strong>Figure 8.</strong> To keep the block coherent, DFlash 2 adds a path selector that picks coherent token sequences across adjacent positions, and local convolutions that reduce acceptance decay toward the end of the block.</figcaption>

DFlash 2 does it with two additions.

- **A path selector picks a coherent sequence.** It scores each adjacent pair of candidates: the drafter's own logit for the candidate, plus a compatibility term that embeds the previous token and the candidate into compact 256-dimensional vectors and matches them under a context gate. Walking the best-scoring path from the last verified token replaces independent guesses, at 2M added parameters and 0.6% latency.
- **Two-tap convolutions keep neighbors consistent.** Inserted before and after each attention and feed-forward sublayer, they mix every position with its predecessor, and the first position reads the last verified token. Attention reads the long-range context, and the convolution handles local consistency inside the block. Reaching one position back recovers most of what ten extra layers would buy: the decay at the block's tail is a local problem, and a local fix is enough.

As we can tell, DFlash 2 raises acceptance length: from 4.92 to 5.97 tokens per verification pass on Qwen3.5-4B, 21% more output than DFlash at 1.3% added latency, and 2.7x to 3.4x throughput over autoregressive decoding on Qwen3.8-27B ([Inco, 2026](https://inco.ai/blog/dflash2/)).

<p class="pullquote">After four generations of speculative decoding architectures, do you have an idea that could be the next SOTA?</p>

</div>

<div id="race" class="section">

### 1.5 Case study: the decoding race

With all 4 models introduced, the race can now run in full comparison. See Figure 9. All 5 models decode the same sentence on the same target model.

<figure class="wide">
<iframe src="../figures/figure6_chalk.html" style="width:100%;height:560px;border:none;" loading="lazy" title="Animated comparison of five speculative decoding approaches"></iframe>
</figure>
<figcaption><strong>Figure 9.</strong> The full decoding race. The EAGLE-3, DFlash, and DSpark lanes use the DeepSpec acceptance lengths on Qwen3-8B (Table 2). DFlash 2's lane uses Inco's reported 2.7–3.4x range.</figcaption>

Tables 2 to 4 collect the reported acceptance lengths on three target models, and the public draft model behind each number so you can rerun it.

<div class="table-wrap">
<table>
<thead>
<tr><th>Method</th><th>τ</th><th>vs baseline</th><th>Draft model</th></tr>
</thead>
<tbody>
<tr><td>EAGLE-3</td><td><span class="num">2.66</span></td><td>baseline</td><td><a href="https://huggingface.co/deepseek-ai/eagle3_qwen3_8b_ttt7">deepseek-ai/eagle3_qwen3_8b_ttt7</a></td></tr>
<tr><td>DFlash</td><td><span class="num">3.11</span></td><td>+17%</td><td><a href="https://huggingface.co/deepseek-ai/dflash_qwen3_8b_block7">deepseek-ai/dflash_qwen3_8b_block7</a></td></tr>
<tr><td>DSpark</td><td><span class="num">3.72</span></td><td>+40%</td><td><a href="https://huggingface.co/deepseek-ai/dspark_qwen3_8b_block7">deepseek-ai/dspark_qwen3_8b_block7</a></td></tr>
<tr><td>DFlash 2</td><td>—</td><td></td><td>none</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 2.</strong> Qwen3-8B. τ is the mean number of accepted tokens per verification pass; "vs baseline" is the gain over EAGLE-3. Source: DeepSpec, MT-Bench, all three drafters trained on the same data.</figcaption>

<div class="table-wrap">
<table>
<thead>
<tr><th>Method</th><th>τ</th><th>vs baseline</th><th>Draft model</th></tr>
</thead>
<tbody>
<tr><td>EAGLE-3</td><td>—</td><td></td><td><a href="https://huggingface.co/yuyijiong/Qwen3.5-4B-Eagle3">yuyijiong/Qwen3.5-4B-Eagle3</a> (community)</td></tr>
<tr><td>DFlash</td><td><span class="num">4.92</span></td><td>baseline</td><td><a href="https://huggingface.co/z-lab/Qwen3.5-4B-DFlash">z-lab/Qwen3.5-4B-DFlash</a></td></tr>
<tr><td>DSpark</td><td><span class="num">5.49</span></td><td>+12%</td><td>not released</td></tr>
<tr><td>DFlash 2</td><td><span class="num">5.97</span></td><td>+21%</td><td>not released</td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 3.</strong> Qwen3.5-4B. Source: Inco blog Table 3, mean over five benchmarks at temperature 1. Inco did not evaluate EAGLE-3 on this model, and the community drafter self-reports on a different harness (three benchmarks, its own sampling settings), so its number is not comparable and DFlash is the baseline instead.</figcaption>

<div class="table-wrap">
<table>
<thead>
<tr><th>Method</th><th>τ</th><th>vs baseline</th><th>Draft model</th></tr>
</thead>
<tbody>
<tr><td>EAGLE-3</td><td>—</td><td></td><td>none</td></tr>
<tr><td>DFlash</td><td>—</td><td></td><td><a href="https://huggingface.co/kstoyanov99/Qwen3.8-27B-Dflash">kstoyanov99/Qwen3.8-27B-Dflash</a> (community)</td></tr>
<tr><td>DSpark</td><td><span class="num">3.62</span></td><td>baseline</td><td><a href="https://huggingface.co/RadixArk/Qwen3.8-27B-DSpark">RadixArk/Qwen3.8-27B-DSpark</a> (community)</td></tr>
<tr><td>DFlash 2</td><td><span class="num">4.80</span></td><td>+33%</td><td><a href="https://huggingface.co/incoai/Qwen3.8-27B-DFlash2">incoai/Qwen3.8-27B-DFlash2</a></td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 4.</strong> Qwen3.8-27B. No EAGLE-3 or DFlash result is reported, so DSpark is the baseline. Source: Inco blog Table 4, mean over five benchmarks, block size 8.</figcaption>

All four models are in production today. Since March 2025, EAGLE-3 draft heads ship for Llama, Qwen, and DeepSeek V3. By spring 2026, DFlash was integrated into SGLang, vLLM, TensorRT-LLM, and llama.cpp, and NVIDIA reported up to 15x throughput with it on Blackwell GPUs ([NVIDIA, 2026](https://developer.nvidia.com/blog/boost-inference-performance-up-to-15x-on-nvidia-blackwell-using-dflash-speculative-decoding/)). DFlash alone has been downloaded more than 3.5 million times in seven months. By mid-2026, model builders release official drafters alongside the models themselves: Meta, Poolside, and NVIDIA for DFlash ([Inco, 2026](https://inco.ai/blog/dflash2/)), Red Hat for DSpark ([RedHatAI, 2026](https://huggingface.co/RedHatAI/GLM-5.2-speculator.dspark-preview)), and in July 2026, Kimi K3 shipped with its own speculator, trained during post-training ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)).

<div class="callout">
<p><strong>When it doesn't help.</strong> Speculative decoding is not free:</p>
<ul>
<li>The draft model takes extra memory. On a machine with little RAM or VRAM, hosting a second model next to the target can cost more than it saves.</li>
<li>Every cycle pays the drafting cost up front. If the draft guesses poorly and acceptance stays low, the speedup can drop below 1x.</li>
<li>Under heavy serving load, the GPU is already saturated by batching, so there is no spare compute for speculation. Engines can disable it at high concurrency.</li>
</ul>
</div>

So far we have covered how speculative decoding works and evolved. In the next section, we will discuss when it stays lossless.

</div>
