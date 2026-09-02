# Writing feedback log — NeurIPS speculative decoding article

Lily's preferences on drafts, recorded as they come. Read before drafting any section.

## 2026-08-31 · §2 transition (bad draft → what she wants)

**Bad:** three paragraphs; re-explained §1's theorem and Table 1; wrote "all six rows belong to the speed family, not one of them looks at what the tokens say."

**Why bad:**
- Over-repeats the previous section. The reader just read it.
- "None of them looks at the tokens" is a judgment, not a fact. This is teaching material and must stay unbiased. No editorial framing, no rhetorical setups ("This is not an oversight"), no universal claims ("every harness in this field").
- Too long for a transition.

**Good preference:**
- One paragraph, mirroring the short intro that sits before §1: state what came before in a clause, then the roadmap of this section.
- Only verifiable statements, each with a citation or a pointer to a table/figure.
- Neutral verbs: "look at", "measure", "verified on", not "notice what is missing".

**Rule going forward:** in §2 every sentence must be either a citation, a reproducible fact, or our own measured result (谁主张谁举证). If a sentence would sound like an accusation to the paper's authors, cut it.

## 2026-08-31 · §2 transition, second pass

**Bad:** "what that guarantee does and does not cover" and "the steps of a production serving stack that fall outside the proof."

**Why bad:** §1 already covered what is guaranteed; §2 focuses only on what is not. "Falls outside the proof" is our framing. The discussed framing (Round 7/11) is: the papers verified lossless on some domains; on the domains they did not verify, we do not know.

**Good preference:**
- Sentence 1: §1 recap in one clause, naming the three factors (T_draft, T_verify, τ) and Table 1.
- Sentence 2: "In this section we look at what lossless does not mean."
- Sentence 3: verified domains held; beyond them, not verified.
- Roadmap uses the three subsection titles verbatim: what lossless doesn't mean in the papers / the boundary is fragile in practice / case study.
- When the plan artifact already has an agreed structure, follow it. Do not re-frame.

## 2026-08-31 · §2.1 opening paragraph (bad → good)

**Bad:** listed each paper's speedup numbers (EAGLE-3 3.0x to 6.5x, DFlash 6.1x, DSpark 16-31% and 60-85%) alongside the datasets.

**Why bad:** the paragraph's point is that every method evaluates on the same kind of benchmarks. The speed numbers are irrelevant to that point and bury it. Piling in every available fact is not thoroughness, it is noise.

**Good preference:**
- Before writing a paragraph, state its one core point. Write only the sentences that carry that point.
- If a table or figure already shows the evidence, the prose summarizes it in one sentence and points to it. Do not repeat the table in prose.
- Concise summary over detail: "all three report on math, code, and chat" beats three sentences of per-paper numbers.

## 2026-08-31 · Figure 8 coverage mapping (bad → good)

**Bad:** colored every Code sub-task (Debugging, Frontend & UI, Shell, File I/O, Code Review) and Q&A as "covered" because they share a macro group with a benchmark.

**Why bad:** the papers never tested those tasks. HumanEval tests function generation, not frontend or debugging; MT-Bench tests conversation, not Q&A. Mapping by macro group inflated coverage from 17% to 44% and would have been an unverifiable claim in a teaching material.

**Good preference:** one benchmark maps to the one task it literally tests. When in doubt, leave the cell grey. Check the coverage claim against what each paper's experiment section actually ran, not against category names.

## 2026-08-31 · Paragraph punchlines (general rule)

**Bad:** the strict-term paragraph opened with "the papers treat lossless as a strict condition" and then two long quotes; the reader could not tell what the quotes were there to prove.

**Good preference:** every paragraph opens with one sentence that states its point in plain words ("Even within these papers, lossless is conditional"). Evidence and quotes follow, trimmed to the clause that carries the point. Close on the consequence, not a definition.

## 2026-08-31 · Medusa bullet (attribution + unverifiable production claims)

**Bad:** (1) "whether Medusa is lossless depends on the temperature" pinned the condition on one method. (2) Added "temperature 1 is where models are served: OpenAI default is 1, Qwen3 recommends 0.6-0.7" to make the condition feel relevant.

**Why bad:** (1) The point is that lossless depends on the setting (temperature, how far the acceptance rule is relaxed), not on Medusa. Attributing it to a method misstates the argument. (2) We do not know whether OpenAI or Qwen serve with speculative decoding or at what temperature. A relevance claim we cannot verify is worse than none.

**Good preference:** state the condition as a property of the setting. Only add "why it matters in production" if we have a source showing speculative decoding running under that exact setting. Logic order per paragraph: fact → what it shows → why.

## 2026-08-31 · §2.2 confidence-threshold (bad → cut)

**Bad:** presented DeepSpec's --confidence-threshold as a scandal ("every unverified token skips the step the proof lives on").

**Why bad:** skipping verification for high-confidence tokens is a normal engineering choice, not a gotcha. Alarmist framing over a routine flag reads as 大惊小怪 and damages credibility. The flag matters only as the dial for 2.3's sweep, where the cost is measured, so introduce it there.

**Good preference:** if a mechanism is standard practice, describe it neutrally or not at all; save it for where we have our own measurement.
