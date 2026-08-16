<div id="measured" class="section">

## 2 · What's Measured?

</div>

<div id="metric" class="section">

### 2.1 · The metric

Speculative decoding reports progress with two numbers. Acceptance length is how many draft tokens the target model accepts per verification step, on average. Tokens per second is the throughput the user feels. The first drives the second, but they are not the same thing: drafting has its own cost, so an acceptance length of 3 does not mean a 3x speedup. Acceptance length counts accepted proposals, not saved passes.

</div>

<div id="theorem" class="section">

### 2.2 · Why is it lossless in theory?

A small draft model proposes K tokens, and the large target model verifies all K in a single forward pass. This works because autoregressive decoding is memory-bandwidth bound. Generating one token streams the entire weight matrix out of HBM while the compute units sit mostly idle, so a forward pass over K tokens costs nearly the same as a pass over one.

Verification uses rejection sampling: each proposed token is accepted with probability \( \min(1, p(x)/q(x)) \), where \(p\) is the target distribution and \(q\) is the draft distribution, and the first rejected position is resampled from a corrected distribution. This procedure guarantees the output distribution is identical to the target model's ([Leviathan et al., 2023](https://arxiv.org/abs/2211.17192); [Chen et al., 2023](https://arxiv.org/abs/2302.01318)). Correctness is guaranteed by construction, so evaluation only has one dimension left to care about, which is efficiency. This theorem is the foundation of how the entire field evaluates itself. It is also the assumption Section 3 examines.

</div>

<div id="generations" class="section">

### 2.3 · Three generations of draft models

Each generation removes the bottleneck of the previous one.

**EAGLE-3** ([Li et al., 2025](https://arxiv.org/abs/2503.01840)) drafts at the feature level instead of the token level. A single trained decoder layer reuses the target model's hidden states and proposes tokens autoregressively. Acceptance improves, but drafting itself is still sequential, one token at a time.

**DFlash** ([Chen et al., 2026](https://arxiv.org/abs/2602.06036)) replaces the autoregressive draft with block diffusion. The draft predicts an entire block of 16 tokens in a single parallel forward pass, with the target's hidden states injected into every draft layer. Drafting stops being the bottleneck.

**DSpark** ([DeepSeek, 2026](https://arxiv.org/abs/2607.05147)) builds on the parallel backbone and adds two things: a small sequential head so later draft tokens can see earlier ones, and a confidence head with a load-aware scheduler that trims low-confidence tokens before verification, saving batch capacity.

<div class="tbd"><span class="tag">TBD</span>Interactive walkthrough component for the web
      version, with adjustable draft length.</div>

</div>

<div id="objective" class="section">

### 2.4 · The metric is also the training objective

How a draft model gets trained explains why acceptance rate dominates evaluation. The Kimi K3 report ([§4.1.4](https://arxiv.org/abs/2607.24653)) describes the current recipe. The target model is frozen. Only a single draft layer and a feature-fusion projection are updated. During training the draft unrolls seven steps and consumes its own outputs, simulating the recurrent drafting it will do at inference time. And the loss is

\[ \mathcal{L}_{LK} = -\log \sum_{x \in \mathcal{V}} \min\big(p(x),\, q(x)\big) \]

which is the negative log of the per-token acceptance probability itself ([Samarin et al., 2026](https://arxiv.org/abs/2602.23881)). The training objective and the evaluation metric are the same number. A draft model is trained to be accepted, and then graded on how often it is accepted.

</div>

<div id="datasets" class="section">

### 2.5 · What the field evaluates on

Where do these numbers come from? [DeepSpec](https://github.com/deepseek-ai/DeepSpec), DeepSeek's open-source training and evaluation stack for draft models, is a representative example. Its evaluation harness runs nine datasets: gsm8k, math500, and aime25 for math; humaneval, mbpp, and livecodebench for code; mt-bench, alpaca, and arena-hard-v2 for conversation. The center of gravity is verifiable, predictable tasks, the kind where the next token is easy to guess.

If acceleration has only ever been evaluated on this narrow a slice of what models do, can we claim the inference is lossless? What happens in the domains nobody measured?

> **Takeaways.** The field reports acceptance length and tokens per second. Speed and acceptance are easy to measure and quality is not, and rejection-sampling verification guarantees the output distribution exactly, so evaluation collapsed to a single efficiency dimension. The training objective converged onto the same number: the LK loss is the negative log of per-token acceptance probability, so drafts are trained on the metric they are graded with. And the evaluation datasets concentrate on verifiable, low-entropy tasks.

</div>
