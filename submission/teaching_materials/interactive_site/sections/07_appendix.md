<div id="appendix" class="section">

## Appendix

We identified a significant gap in the frontend design evaluation under a vendor-assembled stack (fp4 quantization, speculative decoding, KV routing, prefill-decode disaggregation): the same GLM 5.2 model lost 5.6 points, 76.9 to 71.2. Design output is open-ended and hard for a draft to predict. It is absent from the speculative decoding benchmarks. However, frontend and UI tasks carry significant weight in the OpenRouter task usage (Figure 9). In other words, users would receive degraded performance when they use spec models tuned for coding and math only. The other four domains showed no significant gap. The culprit in that stack was quantization, so the measurement says little about speculative decoding on its own.

<figure>
<div class="fig2">
<img src="figures/id673_fp8.png" alt="reference render of the calendar prompt, with the requested translucent popup implemented" /> <img src="figures/id673_fp4.png" alt="accelerated render of the same prompt, a clean page with the calendar popup missing" />
</div>
</figure>
<figcaption><strong>Figure A1.</strong> The same model, the same frontend prompt, left is the original model, right is under the vendor-assembled accelerated stack. The culprit here was quantization.</figcaption>

</div>
