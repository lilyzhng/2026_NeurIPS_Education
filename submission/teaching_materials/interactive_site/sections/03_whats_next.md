<div id="next" class="section">

## 3. What's Next

In this section we go through the exciting new directions for speculative decoding: (3.1) multimodal speculative decoding and (3.2) speculative decoding going from tokens to tool calls.

</div>

<div id="multimodal" class="section" data-toc="3.1 Multimodal speculative decoding">

### 3.1 Multimodal Speculative Decoding

The methods above all target language-only models, but a growing share of decoding workloads is multimodal. A computer-use agent reads a screenshot at every step of its trajectory, whether it is browsing the web or checking its own front-end code, and parsing User uploaded documents, charts, and videos in the chat.

So the question is: can we expect speculative decoding to work for multimodal language models as well?

The answer is not yet: no multimodal speculative decoding method has reached mainstream adoption. vLLM merged its first VLM support for EAGLE-3 (Qwen2.5-VL only) in v0.11.1 ([vLLM #22872](https://github.com/vllm-project/vllm/pull/22872)) while its other speculative paths still reject multimodal models, and SpecForge, SGLang's draft-training framework, lists VLM integration as roadmap ([SpecForge, 2025](https://www.lmsys.org/blog/2025-07-25-spec-forge/)).

On the research side, MMSpec, the first VLM speculative decoding benchmark, measures over 600 samples across ten algorithms ([MMSpec, 2026](https://arxiv.org/abs/2603.14989)), and its main finding is that speculative decoding designed for language models can degrade on multimodal input, because the draft model has limited vision capability compared to the target model. This happens in two ways:

- **Text-only drafters miss the image entirely.** The standard drafter is a small language model with no component for vision input ([MASSV, 2025](https://arxiv.org/abs/2505.10526)).
- **Small VLM does not close the gap.** ViSpec's hypothesis is that a large VLM filters redundant image information layer by layer, while a small model struggles to do the same, so vision capability degrades disproportionately as the drafter shrinks ([ViSpec, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115277)).

The early findings converge on the same design choice: share the target's visual representations with the drafter, rather than training vision capacity into a small model from scratch. MASSV connects the target's own vision encoder to the draft model through a lightweight projector and distills on the target's responses, reaching up to 30% longer accepted length and 1.46x end-to-end speedup over text-only drafting ([MASSV, 2025](https://arxiv.org/abs/2505.10526)). ViSpec trains a vision-aware drafter and reports the first substantial speedups on VLM decoding ([ViSpec, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115277)).

</div>

<div id="toolcalls" class="section" data-toc="3.2 Speculating tool calls">

### 3.2 From Speculating Tokens to Speculating Tool Calls

Speculative decoding so far operates on tokens. The same predict-then-verify idea extends one level up, to tool calls in agents. For an agent, the expensive unit is the tool call: a sub-LLM query or an API request takes seconds, while the code that issues it is still being generated.

Early work has started to formalize this. Speculative Interaction Agents define speculative tool calling as a way to cut time-to-first-token ([Hooper et al., 2026](https://arxiv.org/abs/2605.13360)), and Act While Thinking pre-executes tool calls predicted from patterns in the reasoning trace ([Ji et al., 2026](https://arxiv.org/abs/2603.18897)). A shared benchmark is still missing: each paper evaluates on its own setup, either borrowing OOLONG ([2025](https://arxiv.org/abs/2511.02817)) or building a private task corpus.

Speculative programmatic tool calling is a concrete instantiation ([Zhang, 2026](https://alexzhang13.github.io/blog/2026/spec-ptc/)). While the model is still writing code, a second interpreter runs the partial program and launches any tool call whose inputs are already determined. When the code executes for real, a matching pre-launched call returns its stored result, and a mismatched one is discarded and re-executed. A wrong guess costs only the wasted early launch. On OOLONG with Qwen3-30B, this yields 1 to 1.2x end-to-end speedup.

<p class="pullquote">If agent workloads keep growing, this direction will likely follow the trajectory of token-level speculative decoding: better speculation policies, acceptance rate as a first-class metric, and a shared benchmark to standardize the speedup claims.</p>

</div>
