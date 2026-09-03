<div id="train" class="section">

## 4. Hands-On Lab

</div>

<div id="servefirst" class="section" data-toc="4.1 Serve an accelerated model">

### 4.1 Serve your first accelerated model

In this section you serve the same model twice, once vanilla and once with a speculator, and measure inference acceleration on your own GPU.

The checkpoints come from [DeepSpec](https://github.com/deepseek-ai/DeepSpec), which releases drafts for EAGLE-3, DFlash, and DSpark on the same target, Qwen3-8B. The serving engine is vLLM. The first deployment will have a cold start (image build plus a 16GB weight download, about 10 minutes), but it is cached afterwards, so later experiments are faster.

**Where to get the GPU.** Any H100/A100 works. If you don't have one, get $30 free credits by signing up for a [Modal](https://modal.com) account. That covers this whole lab (an H100 is ~$4/hour, a full afternoon uses $8-12).

```bash
pip install modal && modal setup                    # one-time account link
git clone https://github.com/lilyzhng/2026_NeurIPS_Education && cd */teaching_materials/lab
SPEC_MODE=vanilla modal deploy modal_vllm_serve.py   # prints your server URL
```

The script pins the image, caches model weights in a volume so they download once, and exposes the server at a public URL. When done, `modal app stop neurips-spec-lab` releases the GPU.

Serve the vanilla model:

```bash
vllm serve Qwen/Qwen3-8B --port 8000
```

Send a prompt and measure the generation speed (`measure_decoding_speed.py`). Then restart the server with the DeepSpec DSpark speculator (on Modal: `SPEC_MODE=dspark modal deploy modal_vllm_serve.py`) and run the same bench again:

```bash
vllm serve Qwen/Qwen3-8B --port 8000 --speculative-config \
  '{"model": "deepseek-ai/dspark_qwen3_8b_block7", "method": "dspark", "num_speculative_tokens": 7}'
```

Across 5 runs on one H100, the speedup is stable (mean ± std, Figure 14):

<figure class="mid">
<img src="figures/fig14_runs_h100.svg" alt="Bar chart: vanilla Qwen3-8B decodes 136.3 plus or minus 1.3 tok/s, with the DSpark draft 231.4 plus or minus 4.5 tok/s, a 1.70x speedup" />
</figure>
<figcaption><strong>Figure 14.</strong> Decode throughput of Qwen3-8B on one H100, vanilla vs with the DSpark draft. Mean ± std over 5 runs.</figcaption>

vLLM does not report acceptance length or per-token latency directly. Both come from real measurements: latency from the throughput above, and τ from the server's `/metrics` counters (5,180 draft tokens proposed at 7 per pass = ~740 verification passes for 2,606 generated tokens). See the calculation below:

<div class="sptc-py" data-lang="text"><pre>
L_target = 1 / 136.3 tok/s ≈ 7.3 ms         # latency of the target (vanilla) model, per token
L_dspark = 1 / 231.4 tok/s ≈ 4.3 ms         # latency with the DSpark draft, per token
τ        ≈ 3.5                             # acceptance length
&nbsp;
T_draft + T_verify = L_dspark × τ ≈ 15.1 ms # cost of one draft+verify pass
η = L_target / L_dspark ≈ 1.70x             # speedup
</pre></div>

</div>

<div id="race42" class="section" data-toc="4.2 The decoding race">

### 4.2 The decoding race: algorithms x domains

Now race the algorithms across domains: redeploy with a different draft, rerun the same three-domain prompt set (`race_domains.py`: coding / creative / frontend, 512 tokens each, greedy).

```bash
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py   # config relabel applied in the script
python3 race_domains.py --url <your-url> --label <mode>   # once per deploy
```

Our H100 medians (tok/s, speedup over vanilla):

<div class="table-wrap">
<table>
<thead>
<tr><th>domain</th><th>vanilla</th><th>DSpark</th><th>EAGLE-3</th><th>DFlash (broken config)</th></tr>
</thead>
<tbody>
<tr><td>coding</td><td><span class="num">138.1</span></td><td><span class="num">311.9 (2.3x)</span></td><td><span class="num">158.8 (1.15x)</span></td><td><span class="num">119.1 (0.86x)</span></td></tr>
<tr><td>creative</td><td><span class="num">138.2</span></td><td><span class="num">416.7 (3.0x)</span></td><td><span class="num">229.5 (1.66x)</span></td><td><span class="num">110.3 (0.80x)</span></td></tr>
<tr><td>frontend</td><td><span class="num">137.6</span></td><td><span class="num">333.1 (2.4x)</span></td><td><span class="num">208.2 (1.51x)</span></td><td><span class="num">111.1 (0.81x)</span></td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 4.</strong> The decoding race, measured: three-domain medians per lane. All draft weights are DeepSpec's; the EAGLE-3 lane needs a one-line config relabel to load (acceptance under-tuned, τ ≈ 1.3), and the DFlash column shows a misconfigured lane kept on purpose.</figcaption>

Three readings. Vanilla is flat across domains; the speculators are not: acceptance is domain-conditional, and the same recipe ranks DSpark (τ 3.5) above EAGLE-3 (τ 1.3) on this target. DFlash comes out <em>slower than vanilla</em>, and the metrics counters say why: τ ≈ 1.03, almost every draft token rejected, so the lane pays full drafting cost for nothing. A mismatched drafter costs you speed: benchmark before you swap one in. And a caveat on the creative row: at temperature 0, open-ended prose loops, and repetitive text is easy to draft. Rerun at temperature 0.7 and compare.

</div>

<div id="threshold43" class="section" data-toc="4.3 Break losslessness on purpose">

### 4.3 Break losslessness on purpose

Section 2.1 showed that a relaxed acceptance rule only shifts the output distribution when you sample. So this experiment runs at temperature 1.0, and it runs on SGLang: the acceptance threshold (`--speculative-accept-threshold-single/acc`) is an SGLang serving flag, and vLLM exposes no equivalent. Which engine you serve on decides which lossless-breaking knobs you can even reach. That is Section 2.2 in one sentence.

For each threshold from 1.0 (strict, lossless) to 0.3, `sweep_threshold.py` redeploys the DSpark server, runs a GSM8K subset, and records speed, acceptance length, and accuracy:

```bash
python3 sweep_threshold.py --url <your-sglang-url> --n 30
```

Our H100 results (30 problems, temperature 1.0):

<div class="table-wrap">
<table>
<thead>
<tr><th>threshold</th><th>tokens/s</th><th>τ</th><th>accuracy</th></tr>
</thead>
<tbody>
<tr><td>1.0 (lossless)</td><td><span class="num">127.1</span></td><td><span class="num">3.9</span></td><td><span class="num">0.70</span></td></tr>
<tr><td>0.9</td><td><span class="num">121.2</span></td><td><span class="num">4.8</span></td><td><span class="num">0.53</span></td></tr>
<tr><td>0.7</td><td><span class="num">128.0</span></td><td><span class="num">7.2</span></td><td><span class="num">0.80</span></td></tr>
<tr><td>0.5</td><td><span class="num">127.3</span></td><td><span class="num">4.7</span></td><td><span class="num">0.73</span></td></tr>
<tr><td>0.3</td><td><span class="num">119.4</span></td><td><span class="num">4.4</span></td><td><span class="num">0.73</span></td></tr>
</tbody>
</table>
</div>
<figcaption><strong>Table 5.</strong> Threshold sweep on SGLang + DSpark: acceptance responds, speed stays verification-bound, accuracy stays inside small-sample noise.</figcaption>

The knob bites where theory says it should: acceptance length climbs as the threshold loosens (3.9 to 7.2). What does not appear is the clean speed-up-accuracy-down curve: throughput stays verification-bound at batch size 1, and accuracy at n=30 moves inside its own noise band (0.53 and 0.80 are two draws of the same coin). That absence is the lesson: on a robust domain like GSM8K, the damage from relaxed acceptance hides below small-sample noise, which is exactly why Section 2.3 needed open-ended frontend prompts and a bigger N to see the gap. This fills Figure 12 with real results, error bars and all.

One negative result worth keeping: we first ran this sweep greedy, and every threshold produced identical τ and accuracy: at temperature 0 a draft token is accepted only on exact match, so the threshold never fires. The knob only exists where sampling exists, which is exactly Section 2.1's temperature bullet.

</div>

<div id="figure11task" class="section" data-toc="4.4 The Figure 11 task">

### 4.4 The Figure 11 task, on your own server

Section 2.3 found its frontend gap under a full vendor stack, where quantization was the culprit. Here you isolate one variable: speculative decoding alone, on the same brief Figure 11 used (OpenDesign id 673, "Stunning translucent calendar popup that smoothly blends into the interface").

```bash
python3 generate_frontend_task.py --url <your-url> --label vanilla   # rerun per lane
```

Greedy decoding, so the lossless guarantee makes a concrete prediction: a speculator should reproduce the vanilla HTML exactly. Here is what we measured instead:

<div class="sptc-py" data-lang="text"><pre>
vanilla vs dspark:  identical for 8,299 chars (76% of the page),
                    then diverges at one CSS value:
                    transition: color 0.2s   ->   transition: color 0.3s
                    and the trajectories separate from there (10,924 vs 10,535 chars)
</pre></div>

This is not the theorem failing. The guarantee is about distributions, not trajectories: the speculative path runs different kernels, the numerics shift by a hair, and a near-tie token (0.2s vs 0.3s was evidently one) falls the other way. vLLM's own docs drew this boundary in Section 2.2: theoretical losslessness holds "up to the precision limits of hardware numerics," and output stability is layer three, the one nobody guarantees. Both pages render, both satisfy the brief, and they are different pages. If your product depends on reproducing an exact output, lossless-in-distribution is not the property you think it is.

Then the open exercise: swap in prompts from a domain nobody measured (OpenRouter's other 83%), rerun the race and the sweep, and report three numbers together: acceptance rate, task correctness, domain coverage. If the numbers move this much when the domain changes, what else moved that acceptance rate cannot see?

</div>
