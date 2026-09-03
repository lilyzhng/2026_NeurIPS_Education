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

Across 5 runs on one H100, the speedup is stable (mean ± std, Figure 16):

<figure class="mid">
<img src="figures/fig14_runs_h100.svg" alt="Bar chart: vanilla Qwen3-8B decodes 136.3 plus or minus 1.3 tok/s, with the DSpark draft 231.4 plus or minus 4.5 tok/s, a 1.70x speedup" />
</figure>
<figcaption><strong>Figure 16.</strong> Decode throughput of Qwen3-8B on one H100, vanilla vs with the DSpark draft. Mean ± std over 5 runs.</figcaption>

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

### 4.2 The decoding race

In this section you watch four deployments race on the same prompt: the vanilla model against EAGLE-3, DFlash, and DSpark, all on H100. The point is to let the reader get a sense of what inference acceleration does on real-world tasks.

```bash
SPEC_MODE=eagle3 modal deploy modal_vllm_serve.py
SPEC_MODE=dspark modal deploy modal_vllm_serve.py
modal run modal_dflash_offline.py            # DFlash lane, see note below
python3 build_race_demo.py                   # assembles the demo from your outputs
```

These commands reproduce the two live demos in Section 2.3 (Figures 11 and 12).

Look closely at Figure 11 in Section 2.3: the four lanes did not generate the same page, or even the same number of tokens. Vanilla produced 1,282 tokens on the calendar brief, the accelerated lanes 1,127 to 1,185. DFlash finished fastest, and its calendar came out visibly broken.

Figure 12 is the evaluation result on the creative writing task: EAGLE-3 and DSpark wrote identical stories, while vanilla and DFlash each took a different trajectory from the same opening line. That leaves three distinct stories to judge:

| story | instruction following | Latin vocabulary | writing style |
|---|---|---|---|
| vanilla · 7/10 | 979 words. Ends entering the fight, close to violating the no-combat rule. | Correct, restrained. | Strongest sensory detail. Named cast. Ending falls back on a generic freedom monologue. |
| EAGLE-3 / DSpark · 6/10 | Best. 998 words, all constraints met. | Correct, sparse. | Weakest as fiction. Restates one thesis three times. No named characters. Explains politics rather than dramatizing it. |
| DFlash · 7.5/10 | Worst. 1,092 words, 9% over. Invents a sacrae bell. | Inaccurate, decorative. | Best structure. Full dawn-to-night arc, one side character with a backstory, strongest closing image. |

**Table 4.** The three distinct gladiator stories, judged on the brief's own constraints. Same target model, greedy decoding: the differences are trajectory divergence, not different models.

Overall, DFlash wins. Fiction lives on shape and character before compliance, and DFlash is the only story that delivers a complete day, a side character you remember, and a closing image that lands. Its violations are copyedit-level fixes. EAGLE-3 and DSpark followed every rule and produced the piece you forget first.

The cross-domain twist: DFlash wrote the worst calendar page and the best story. A lane's trajectory can land well in one domain and badly in another, and nothing in the serving stack tells you which you got.

Why do EAGLE-3 and DSpark match in writing and front end code, while DFlash stands apart? EAGLE-3 and DSpark share DeepSpec's training data, propose similar tokens. DFlash differs in training data, block size, and serving path, so the exact cause cannot be ruled out here, but likely caused by the difference in training data.

<sub>Note: `vllm serve` crashes on DFlash in stable 0.28.0, and only the offline `LLM()` path is CI-tested, so `modal_dflash_offline.py` runs this way. Its draft is also the z-lab release rather than DeepSpec's.</sub>

</div>
