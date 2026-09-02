# 3. What's Next

<!-- 定位：acceleration 移进 training（ownership）；speculation 往 harness 层扩散（Alex Zhang sPTC 引用位，https://alexzhang13.github.io/blog/2026/spec-ptc/）；quality-aware draft training 不存在。 -->

## 定稿

（待写）

## 旧版素材（原 What's Next 全文，改写来源）

> <div id="next" class="section">
> 
> ## 4 · What's Next?
> 
> </div>
> 
> <div id="ownership" class="section">
> 
> ### 4.1 · Acceleration is moving into training
> 
> The industry is already answering part of the question, not by fixing the eval but by moving the acceleration to where it can be validated before release. DeepSeek pushed FP8 into pre-training with DeepSeek-V3 ([DeepSeek-AI, 2024](https://arxiv.org/abs/2412.19437)). gpt-oss shipped MXFP4 weights with quantization-aware training ([OpenAI, 2025](https://arxiv.org/abs/2508.10925)). K2-Thinking reported every benchmark number at INT4, making the quantized model the official model. Kimi K3 ships the speculator itself: the draft model is fine-tuned as part of post-training, against the deployment-precision target, and validated before the model leaves the factory ([Kimi Team, 2026](https://arxiv.org/abs/2607.24653)).
> 
> <div class="tbd"><span class="tag">TBD</span>Figure: timeline of acceleration moving from the
>       serving layer into training, adapted from LosslessBench Figure 6.</div>
> 
> This is why the ownership split in Section 3.2 produced a 0.3-point loss on one side and a 5.6-point loss on the other. When the model owner trains and validates the acceleration, the accelerated model is the released model, and there is nothing left for a serving vendor to bolt on unverified. When acceleration is assembled downstream by whoever hosts the model, the lossless claim belongs to no one, and no one checks it. Whoever owns the acceleration owns the quality.
> 
> </div>
> 
> <div id="traininggap" class="section">
> 
> ### 4.2 · The training objective nobody has built
> 
> Ownership fixes who validates. It does not change what the draft is trained for. Every published draft-training objective optimizes alignment with the target or acceptance itself: distillation on target outputs in DistillSpec ([Zhou et al., 2024](https://arxiv.org/abs/2310.08461)), feature regression in EAGLE-3 ([Li et al., 2025](https://arxiv.org/abs/2503.01840)), and the LK loss that directly maximizes per-token acceptance ([Samarin et al., 2026](https://arxiv.org/abs/2602.23881)). No published objective trains a draft to preserve the target's behavior on the long tail, the high-entropy domains where Section 3.4 showed acceptance is weakest and verification is thinnest. The closest published work operates at the verification layer instead: Judge Decoding ([Bachmann et al., 2025](https://arxiv.org/abs/2501.19309)) trains the verifier to accept tokens that differ from the target but preserve quality. Quality-aware draft training does not exist yet.
> 
> </div>
> 
> <div id="proposal" class="section">
> 
> ### 4.3 · Proposal
> 
> The evaluation fix is smaller than the training fix, and available today: report behavior alongside speed. A speculative-decoding eval should publish three numbers together, acceptance rate, task correctness on the same generations, and the domain coverage of the prompt set. The first is what the field already reports. The second costs one grading pass over outputs the harness already produces. The third is a list of names. Section 5 shows that a single afternoon and one GPU are enough to produce all three.
> 
> > **Open questions.** What does a draft-training objective that weights long-tail behavior look like, and does it cost acceptance rate? When acceleration ships inside the model, who audits the model owner's own lossless claim? And acceptance rate is domain-conditional; is there a principled way to choose the domain mix of a speculative-decoding eval, rather than inheriting whatever benchmarks are nearby?
> 
> </div>
