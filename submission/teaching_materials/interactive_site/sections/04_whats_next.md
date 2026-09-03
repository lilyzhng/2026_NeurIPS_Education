<div id="next" class="section">

## 3. What's Next

Section 2 brought awareness of lossy inference. In this section we go through the exciting new directions for speculative decoding: (3.1) multimodal speculative decoding, (3.2) speculative decoding going from tokens to tool calls, and (3.3) inference acceleration ownership.

</div>

<div id="multimodal" class="section" data-toc="3.1 Multimodal speculative decoding">

### 3.1 Multimodal Speculative Decoding

The methods above all target language-only models, but a growing share of decoding workloads is multimodal. A computer-use agent reads a screenshot at every step of its trajectory, whether it is browsing the web or checking its own front-end code, and in chat the same vision-language models parse user-uploaded documents, charts, and videos.

So the question is: can we expect speculative decoding to work for multimodal language models as well?

The answer is not yet: no multimodal speculative decoding method has reached mainstream adoption. vLLM merged its first VLM support for EAGLE-3 (Qwen2.5-VL only) in v0.11.1 ([vLLM #22872](https://github.com/vllm-project/vllm/pull/22872)) while its other speculative paths still reject multimodal models, and SpecForge, SGLang's draft-training framework, lists VLM integration as roadmap ([SpecForge, 2025](https://www.lmsys.org/blog/2025-07-25-spec-forge/)).

On the research side, MMSpec, the first VLM speculative decoding benchmark, measures over 600 samples across ten algorithms ([MMSpec, 2026](https://arxiv.org/abs/2603.14989)), and its main finding is that speculative decoding designed for language models can degrade on multimodal input, because the draft model has limited vision capability compared to the target model. This happens in two ways:

- **Text-only drafters miss the image entirely.** The standard drafter is a small language model with no component for vision input ([MASSV, 2025](https://arxiv.org/abs/2505.10526)).
- **Small VLM does not close the gap.** ViSpec's hypothesis is that a large VLM filters redundant image information layer by layer, while a small model struggles to do the same, so vision capability degrades disproportionately as the drafter shrinks ([ViSpec, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115277)).

Either way, the draft diverges from the vision-conditioned target and acceptance drops.

The early findings converge on the same design choice: share the target's visual representations with the drafter, rather than training vision capacity into a small model from scratch. MASSV connects the target's own vision encoder to the draft model through a lightweight projector and distills on the target's responses, reaching up to 30% longer accepted length and 1.46x end-to-end speedup over text-only drafting ([MASSV, 2025](https://arxiv.org/abs/2505.10526)). ViSpec trains a vision-aware drafter and reports the first substantial speedups on VLM decoding ([ViSpec, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115277)).

</div>

<div id="toolcalls" class="section" data-toc="3.2 Speculating tool calls">

### 3.2 From Speculating Tokens to Speculating Tool Calls

Speculative decoding so far operates on tokens. The same predict-then-verify idea extends one level up, to tool calls in agents. For an agent, the expensive unit is the tool call: a sub-LLM query or an API request takes seconds, while the code that issues it is still being generated.

Early work has started to formalize this. Speculative Interaction Agents define speculative tool calling as a way to cut time-to-first-token ([Hooper et al., 2026](https://arxiv.org/abs/2605.13360)), and Act While Thinking pre-executes tool calls predicted from patterns in the reasoning trace ([Ji et al., 2026](https://arxiv.org/abs/2603.18897)). A shared benchmark is still missing: each paper evaluates on its own setup, either borrowing OOLONG ([2025](https://arxiv.org/abs/2511.02817)) or building a private task corpus.

Speculative programmatic tool calling is a concrete instantiation ([Zhang, 2026](https://alexzhang13.github.io/blog/2026/spec-ptc/)). While the model is still writing code, a second interpreter runs the partial program and launches any tool call whose inputs are already determined. When the code executes for real, a matching pre-launched call returns its stored result, and a mismatched one is discarded and re-executed. A wrong guess costs only the wasted early launch. On OOLONG with Qwen3-30B, this yields 1 to 1.2x end-to-end speedup.

<u>If agent workloads keep growing, this direction will likely follow the trajectory of token-level speculative decoding: better speculation policies, acceptance rate as a first-class metric, and a shared benchmark to standardize the speedup claims.</u>

</div>

<div id="ownership" class="section" data-toc="3.3 Inference acceleration ownership">

### 3.3 Should the Lab Own Inference Acceleration?

Step by step, acceleration is moving from the serving layer into frontier labs. DeepSeek pushed FP8 into pre-training with DeepSeek-V3 ([DeepSeek-AI, 2024](https://arxiv.org/abs/2412.19437)). OpenAI shipped gpt-oss MXFP4 weights with quantization-aware training ([OpenAI, 2025](https://arxiv.org/abs/2508.10925)). K2-Thinking reported every benchmark number at INT4, making the quantized model the official model. Kimi K3 has the draft model fine-tuned as part of post-training, and validated before the model leaves the lab ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)).

<figure>
<img src="figures/fig13_ownership_migration.png" alt="Timeline of acceleration work migrating from the serving layer into the labs, 2025 to 2026" />
</figure>
<figcaption><strong>Figure 13 (mock).</strong> The model layer absorbs acceleration step by step. The room left for serving shrinks toward one job: serve. From <a href="https://lilyzh.ng/writing/losslessbench/">LosslessBench</a> Figure 6, boundary redrawn as steps.</figcaption>

See Figure 13. Each step, from 2025 to 2026, shows frontier labs owning more of the inference acceleration space. The work used to be owned by the serving layer. An inference provider would take the released FP8 weights, quantize them, train a draft model on top, and serve it on OpenRouter for the general public. This meant the inference layer owned the quality evaluation. But now, the labs do this work themselves and validate it before the model ships, leaving less room for the inference layer ([LosslessBench](https://lilyzh.ng/writing/losslessbench/), Figure 6).

<u>This ownership shift fixes the missing quality validation: the lab validates the accelerated model before it ships, closing the gap Section 2 described.</u>

</div>
