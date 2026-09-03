# Parked: 4.3 threshold sweep (2026-09-03)

Pulled from the 定稿 pending redesign (frontend A/B at threshold 1.0 vs 0.3 instead of the GSM8K table). Data: data/4_3_sweep.json, script: lab/sweep_threshold.py.

### 4.3 A loose acceptance threshold can break losslessness（定稿骨架 2026-09-03，重写排队中：frontend A/B 换主展品，GSM8K 表降级为对照）

Section 2.1 showed that a relaxed acceptance rule only shifts the output distribution when you sample. So this experiment runs at temperature 1.0, and it runs on SGLang: the acceptance threshold (`--speculative-accept-threshold-single/acc`) is an SGLang serving flag, and vLLM exposes no equivalent. Which engine you serve on decides which lossless-breaking knobs you can even reach. That is Section 2.2 in one sentence.

For each threshold from 1.0 (strict, lossless) to 0.3, `sweep_threshold.py` redeploys the DSpark server, runs a GSM8K subset, and records speed, acceptance length, and accuracy:

```bash
python3 sweep_threshold.py --url <your-sglang-url> --n 30
```

Our H100 results (30 problems, temperature 1.0):

| threshold | tokens/s | τ | accuracy |
|---|---|---|---|
| 1.0 (lossless) | 127.1 | 3.9 | 0.70 |
| 0.9 | 121.2 | 4.8 | 0.53 |
| 0.7 | 128.0 | 7.2 | 0.80 |
| 0.5 | 127.3 | 4.7 | 0.73 |
| 0.3 | 119.4 | 4.4 | 0.73 |

**Table 5.** Threshold sweep on SGLang + DSpark: acceptance responds, speed stays verification-bound, accuracy stays inside small-sample noise.

The knob bites where theory says it should: acceptance length climbs as the threshold loosens (3.9 to 7.2). What does not appear is the clean speed-up-accuracy-down curve: throughput stays verification-bound at batch size 1, and accuracy at n=30 moves inside its own noise band (0.53 and 0.80 are two draws of the same coin). That absence is the lesson: on a robust domain like GSM8K, the damage from relaxed acceptance hides below small-sample noise, which is exactly why Section 2.3 needed open-ended frontend prompts and a bigger N to see the gap. This fills Figure 12 with real results, error bars and all.

One negative result worth keeping: we first ran this sweep greedy, and every threshold produced identical τ and accuracy: at temperature 0 a draft token is accepted only on exact match, so the threshold never fires. The knob only exists where sampling exists, which is exactly Section 2.1's temperature bullet.

