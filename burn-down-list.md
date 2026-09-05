# Spec Neurips Burndown List

🟢 done · 🟡 ongoing · 🔴 todo

## Submission

| # | Action item | Status / Owner | Completion notes |
|---|---|---|---|
| S1 | Modify the 2-page summary to reflect the new changes from the interactive website | 🟢 Lily | Done 9/4 3:00pm: abstract, concept summary (progression bullets + contributions), objectives, grounding all rewritten; 2 pages |
| S1.1 | Fix Learning Objective #3: confidence → acceptance threshold; drop unsupported claim | 🟢 Lily | Done 9/4 3:00pm: objectives fully rewritten (6 items, reordered) |
| S1.2 | Rewrite Teaching Materials Summary | 🟢 Lily | Done 9/4 3:00pm: website + acceptance-rate demo + lab; progression moved into Concept Summary bullets |
| S1.3 | Rewrite Concept Summary from current website content | 🟢 Lily | Done 9/4 3:00pm: 4 progression bullets + contributions paragraph (LosslessBench, 17% traffic, τ +48% sweep) |
| S1.4 | Rewrite Abstract | 🟢 Lily | Done 9/4 3:00pm: impact-first opening (bottleneck → production), lab described accurately |
| S1.5 | Recompile PDF, verify 2-page limit | 🟢 Lily | Done 9/4 3:00pm: exactly 2 pages; refs pruned to cited-only, 3-column |
| S2 | OpenReview final submission: form + 2-page PDF + site link. Target within the hour, deadline Sep 4 AoE | 🟢 Lily | Submitted 9/4 ~3:45pm: PDF (2 pages) + teaching_materials.zip (5.7MB, site + notebook lab + losslessbench) + form fields incl. 225-char TLDR |
| S2.1 | Audit OpenReview form for the same stale claims (confidence threshold, opposite-directions sweep, grade-the-outputs) and sync with S1 rewrites | 🟢 Lily | Done 9/4 3:05pm: TLDR, concept (195 words), objectives, grounding, teaching summary all synced to final tex |

## Interactive website

| # | Action item | Status / Owner | Completion notes |
|---|---|---|---|
| I1 | Chalkboard figures: apply Figure 1's fix to the rest (20% smaller, dark forest background, chalkboard eraser replay button) | 🟡 Madison |  |
| I2 | Run losslessbench-100 on EAGLE-3 and DSpark. DFlash2 result done, prepared in Figure 11 | 🟡 Lily |  |
| I3 | Section 3.3 deleted (focused-explainer trim, per chairs' reply + Andrew). Spec-tool section kept with learning objective | 🟢 Lily |  |
| I4 | Venue lineage sentence in intro (blockwise parallel decoding NeurIPS 2018, spec decoding ICML 2023, EAGLE-3 NeurIPS 2025, DFlash ICML 2026), per chair guidance | 🟢 Lily |  |
| I5 | Push all the chalkboard figures to GitHub | 🟡 Madison |  |
| I6 | Hover glossary for jargon terms in "What lossless means" (B200, SGLang, vanilla), per Andrew's feedback | 🔴 Madison |  |
| I7 | Mobile + cross-browser pass on the interactive demos (race iframes, replay buttons, Figure 12 SVG) | 🔴 Madison |  |
| I8 | Link check across the site: all external links resolve (HF dataset, arXiv, OpenAI/Anthropic/DeepSeek refs) | 🔴 Madison |  |
| I9 | New 2.4 lab subsection "Adjust acceptance rate yourself" (Figure 17): sweep SGLang acceptance threshold, show quality vs acceptance | 🟢 Lily | Shipped 9/4 2:10pm: swept 1.0 → 0.4 on the frontend design task (L101, temperature 1), τ 4.9 → 7.2; side-by-side generated pages, judged visually; greedy sweep was inert (byte-identical), documented in 2.4 |
| I10 | Figure fixes (rest of site looks good; numbers current as of 9/4 renumber): Figure 2 — Veo 3 block has a disjoint part after fuse; Figure 7 — needs fixing; Figure 9 — stretched on phone view | 🔴 Madison |  |

## Feedbacks

| # | Action item | Status / Owner | Completion notes |
|---|---|---|---|
| F1 | Chairs replied: they prefer a focused explainer on a single concept. Trim accordingly | 🟡 Lily |  |
| F2 | Reply to Daniela: asked if non-NeurIPS venues (ICML lineage) are in scope | 🟢 Lily |  |
| F3 | Collect feedback from Ali | 🟡 Madison |  |
| F4 | Collect feedback from Philip | 🟡 Madison |  |
| F5 | Collect feedback from Andrew — [andrew_feedback](https://docs.google.com/document/d/1-JzSlq5EH-eFcXOoyJ7S7wlD-T8k_i9a6zVXtw9ZzZI/edit?usp=sharing) | 🟢 Lily |  |
| F6 | Collect feedback from Zhijian Liu / Chenyang | 🟡 Lily |  |

## Post-submission (P1, not needed today)

| # | Action item | Status / Owner | Completion notes |
|---|---|---|---|
| P1 | Glossary: one term list (term + one-line definition), two outputs: hover tooltips in the article (see I6) + appendix glossary table as a study handout | 🔴 Lily + Madison |  |
| P2 | Video walkthrough of the site + lab (restores the dropped promise as an asset) | 🔴 Lily |  |
| P3 | Full lossless500 run (eagle3 / dspark / dflash across the five axes), upgrade Figure 10/11 from pilot to full | 🔴 Lily |  |
| P4 | Reply-driven trims after Daniela answers the ICML-scope question | 🔴 Lily |  |
| P5 | Moved to I9 (threshold-sweep lab subsection) | 🟢 — |  |
