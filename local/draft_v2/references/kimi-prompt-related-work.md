# Prompt for Kimi: 整理四篇 related work

把下面这段直接复制给 Kimi。

---

Please archive the following 4 papers/articles into a clean local reference library.

**Target directory:** `~/Documents/lily-memory/Learn/conferences/2026_NeurIPS_Education/local/draft_v2/related_work/`

**The 4 sources:**

1. **EAGLE-3** — "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test" — https://arxiv.org/abs/2503.01840
2. **DFlash** — block-parallel diffusion drafting for speculative decoding — https://arxiv.org/abs/2602.06036
3. **DSpark** — DeepSeek, confidence-scheduled speculative decoding — https://arxiv.org/abs/2607.05147
4. **DFlash 2** — Inco blog post — https://inco.ai/blog/dflash2/

**Required structure (one subfolder per source):**

```
related_work/
├── eagle3/
│   ├── eagle3.md          # full text as clean markdown
│   └── figures/           # all figures as png, named fig1.png, fig2.png, ... (or keep original names)
├── dflash/
│   ├── dflash.md
│   └── figures/
├── dspark/
│   ├── dspark.md
│   └── figures/
└── dflash2/
    ├── dflash2.md
    └── figures/
```

**Rules:**

1. For arXiv papers, prefer the HTML version (`https://arxiv.org/html/<id>` or ar5iv `https://ar5iv.labs.arxiv.org/html/<id>`) for text extraction; fall back to PDF extraction if HTML is unavailable.
2. The `.md` file must contain the FULL text (abstract through conclusion, including section headers), not a summary. Preserve section structure as markdown headers. Math can stay as LaTeX inline (`$...$`).
3. Download every figure image into the `figures/` subfolder, and reference each one inline in the `.md` at the position it appears, as `![Figure N: caption](./figures/figN.png)` with the original caption text.
4. Keep tables as markdown tables.
5. At the top of each `.md`, add a small metadata block: title, authors, date, source URL, and the one-line claim of the paper.
6. Do NOT paraphrase, editorialize, or shorten. This is an archive, not notes.
7. When done, print a tree of what was created and flag anything that failed to download.
