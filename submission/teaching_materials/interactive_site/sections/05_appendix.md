<div id="appendix" class="section">

## Appendix

</div>

<div id="glossary" class="section" data-toc="A.1 Glossary">

<h3 class="glossary-heading">Glossary</h3>

<dl class="glossary-list">
<dt>Acceptance length (τ)</dt><dd>The average number of draft tokens the target model accepts each time it checks a batch, counting the extra token it adds itself.</dd>
<dt>Acceptance rate (α)</dt><dd>How often a proposed draft token passes the target model's check. The more the draft agrees with the target, the higher it is.</dd>
<dt>Acceptance threshold</dt><dd>A serving setting for how strictly draft tokens are checked. At 1.0 the check is exact; lowering it lets more draft tokens through.</dd>
<dt>Autoregressive decoding</dt><dd>Generating text one token at a time, with each token depending on the one before it.</dd>
<dt>Block diffusion</dt><dd>Predicting a whole block of masked tokens at once, instead of one token at a time.</dd>
<dt>Bonus token</dt><dd>The one extra token the target model produces itself each time it checks the draft.</dd>
<dt>Draft model</dt><dd>A cheaper model or draft layer that proposes several likely next tokens.</dd>
<dt>Forward pass</dt><dd>Running the model on its current input to produce scores for possible next tokens.</dd>
<dt>Greedy decoding</dt><dd>Always picking the single most likely next token, so the same prompt gives the same output.</dd>
<dt>KV cache</dt><dd>Stored attention information from earlier tokens that lets the model avoid recomputing the whole context.</dd>
<dt>Lossless</dt><dd>The model produces the same distribution of outputs as the unaccelerated version.</dd>
<dt>MASK token</dt><dd>A placeholder slot in a draft block that the model fills in with a predicted token.</dd>
<dt>Probability distribution</dt><dd>The model's probabilities over all possible next tokens.</dd>
<dt>Quantization</dt><dd>Storing model weights with fewer bits to make inference faster and cheaper, sometimes with accuracy loss.</dd>
<dt>Rejection sampling</dt><dd>A method that accepts or replaces draft tokens so the final outputs still follow the target model's distribution.</dd>
<dt>Speculative decoding</dt><dd>A generation method that uses a fast smaller draft model to propose several tokens, which are then verified by a larger slower target model.</dd>
<dt>Target model</dt><dd>The larger model whose output distribution we want to preserve.</dd>
<dt>Temperature</dt><dd>A setting for how random sampling is. At 0 the model always picks its top choice; at 1 it samples with its natural randomness.</dd>
<dt>Total variation distance</dt><dd>A measure of how different two sets of probabilities are. The closer the draft's guesses are to the target's, the more tokens get accepted.</dd>
<dt>Vanilla model</dt><dd>The target model running without any acceleration, used as the speed baseline.</dd>
</dl>

</div>

<div id="frontend-gap" class="section" data-toc="A.2 Frontend gap under a vendor stack">

### A.2 Frontend gap under a vendor-assembled stack

We identified a significant gap in the frontend design evaluation under a vendor-assembled stack (fp4 quantization, speculative decoding, KV routing, prefill-decode disaggregation): the same GLM 5.2 model lost 5.6 points, 76.9 to 71.2. Design output is open-ended and hard for a draft to predict. It is absent from the speculative decoding benchmarks. However, frontend and UI tasks carry significant weight in the OpenRouter task usage (Figure 9). In other words, users would receive degraded performance when they use spec models tuned for coding and math only. The other four domains showed no significant gap. The culprit in that stack was quantization, so the measurement says little about speculative decoding on its own.

<figure>
<div class="fig2">
<img src="figures/id673_fp8.png" alt="reference render of the calendar prompt, with the requested translucent popup implemented" /> <img src="figures/id673_fp4.png" alt="accelerated render of the same prompt, a clean page with the calendar popup missing" />
</div>
</figure>
<figcaption><strong>Figure A2.</strong> The same model, the same frontend prompt, left is the original model, right is under the vendor-assembled accelerated stack. The culprit here was quantization.</figcaption>

</div>

<div id="ownership" class="section" data-toc="A.3 Inference acceleration ownership">

### A.3 Should the Lab Own Inference Acceleration?

Step by step, acceleration is moving from the serving layer into frontier labs. DeepSeek pushed FP8 into pre-training with DeepSeek-V3 ([DeepSeek-AI, 2024](https://arxiv.org/abs/2412.19437)). OpenAI shipped gpt-oss MXFP4 weights with quantization-aware training ([OpenAI, 2025](https://arxiv.org/abs/2508.10925)). K2-Thinking reported every benchmark number at INT4, making the quantized model the official model. Kimi K3 has the draft model fine-tuned as part of post-training, and validated before the model leaves the lab ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)).

<figure class="plain">
<img src="figures/fig14_ownership_migration.svg" alt="Timeline of acceleration work migrating from the serving layer into the labs, 2025 to 2026" />
</figure>
<figcaption><strong>Figure A3.</strong> The model layer absorbs acceleration step by step. The room left for serving shrinks toward one job: serve. From <a href="https://lilyzh.ng/writing/losslessbench/">LosslessBench</a> Figure 6, boundary redrawn as steps.</figcaption>

See Figure A3. Each step, from 2025 to 2026, shows frontier labs owning more of the inference acceleration space. The work used to be owned by the serving layer. An inference provider would take the released FP8 weights, quantize them, train a draft model on top, and serve it on OpenRouter for the general public. This meant the inference layer owned the quality evaluation. But now, the labs do this work themselves and validate it before the model ships, leaving less room for the inference layer ([LosslessBench](https://lilyzh.ng/writing/losslessbench/), Figure 6).

<u>This ownership shift fixes the missing quality validation: the lab validates the accelerated model before it ships, closing the gap Section 2 described.</u>

</div>
