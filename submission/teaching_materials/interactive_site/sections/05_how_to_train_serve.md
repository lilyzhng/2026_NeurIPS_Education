<div id="train" class="section">

## 4. How to Train + Serve

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

Our 5 runs on one H100:

<div class="table-wrap">
<table>
<thead>
<tr><th>run</th><th>vanilla (tok/s)</th><th>DSpark (tok/s)</th></tr>
</thead>
<tbody>
<tr><td>1</td><td><span class="num">135.1</span></td><td><span class="num">230.3</span></td></tr>
<tr><td>2</td><td><span class="num">136.2</span></td><td><span class="num">234.9</span></td></tr>
<tr><td>3</td><td><span class="num">135.0</span></td><td><span class="num">223.9</span></td></tr>
<tr><td>4</td><td><span class="num">138.1</span></td><td><span class="num">234.0</span></td></tr>
<tr><td>5</td><td><span class="num">136.9</span></td><td><span class="num">233.9</span></td></tr>
<tr><td><strong>median</strong></td><td><span class="num"><strong>136.2</strong></span></td><td><span class="num"><strong>233.9 (1.72x)</strong></span></td></tr>
</tbody>
</table>
</div>

vLLM does not report acceptance length or per-token latency directly. Both come from real measurements: latency from the throughput above, and τ from the server's `/metrics` counters (5,180 draft tokens proposed at 7 per pass = ~740 verification passes for 2,606 generated tokens). See the calculation below:

<div class="sptc-py" data-lang="text"><pre>
L_target = 1 / 136.2 tok/s ≈ 7.3 ms         # latency of the target (vanilla) model, per token
L_dspark = 1 / 233.9 tok/s ≈ 4.3 ms         # latency with the DSpark draft, per token
τ        ≈ 3.5                             # acceptance length
&nbsp;
T_draft + T_verify = L_dspark × τ ≈ 15.0 ms # cost of one draft+verify pass
η = L_target / L_dspark ≈ 1.72x             # speedup
</pre></div>

</div>
