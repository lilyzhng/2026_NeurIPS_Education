# 4. How to Train, Serve, and Test It

<!-- 定位（Round 29）：读者复现 §2 的结果，故意与 §2 重合 = reproduce 闭环。8/23 决定：用 SGLang 重写（现素材是 vLLM），train + serve + evaluate 都做，EAGLE 路线小 draft model，租卡成本几块钱，不加 multimodal。 -->

## 定稿

（待写）

## 旧版素材（原 Hands-on Lab 全文，vLLM 版，待改 SGLang）

> <div id="runit" class="section">
> 
> ## 5 · Hands-on Lab
> 
> Serve and verify a draft model on your own. One GPU is enough.
> 
> ### 5.1 · Serve an accelerated model
> 
> One command starts Qwen3-8B with its official EAGLE-3 draft head:
> 
>     vllm serve Qwen/Qwen3-8B -tp 1 \
>       --speculative-config '{"model": "RedHatAI/Qwen3-8B-speculator.eagle3",
>                              "num_speculative_tokens": 3, "method": "eagle3"}'
> 
> Send it a few prompts and read the acceptance metrics vLLM logs per request. The [model card](https://huggingface.co/RedHatAI/Qwen3-8B-speculator.eagle3) reports an acceptance length of 2.4 to 2.8 on a single A100; your numbers should land in that range on coding prompts and lower on open-ended ones. That difference is Section 3.4 showing up on your own hardware.
> 
> ### 5.2 · Compare three generations of drafts (Section 2.3)
> 
> [DeepSpec](https://github.com/deepseek-ai/DeepSpec) releases trained checkpoints for EAGLE-3, DFlash, and DSpark on the same targets (Qwen3-4B/8B/14B), so the three-generation comparison needs no training. Point the evaluation at each checkpoint in turn and compare acceptance length on the same prompt set.
> 
> <div class="tbd"><span class="tag">TBD</span>Exact commands and our measured table.</div>
> 
> ### 5.3 · Sweep the confidence threshold (Section 3.3)
> 
> Using the DeepSpec evaluation harness, sweep `--confidence-threshold` over a range of values on gsm8k prompts. For each run, keep the generated answers and grade them for correctness in a separate pass. Plot acceptance rate against task accuracy.
> 
> <div class="tbd"><span class="tag">TBD</span>Sweep script and grading script, with the
>       resulting curve.</div>
> 
> ### 5.4 · Exercise: pick a domain nobody measured
> 
> Swap the prompt set for one outside math and code, creative writing, an agent trace, or a frontend task, and rerun 5.1. Watch what happens to acceptance length, then ask the question this article ends on: if the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?
> 
> </div>
