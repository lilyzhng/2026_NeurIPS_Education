# Vibhu's Feedback — 2026-09-04 (RCS thread with Madison)

All feedback from Vibhu Sapra on the interactive site, one item per row, with status. Verbatim quotes preserved; raw transcript at the bottom. He also plans to leave comments on Google Docs.

## Intro & framing

| # | Feedback | His words | Status |
|---|---|---|---|
| 1 | Section 1's content was the architectural evolution, but the title said "What lossless means"; change the title | why are we spending so much time defining lossless? ... > no, is lossless meaning __ > ok move on | ✅ Done 9/4: Section 1 retitled "How speculative decoding evolved"; arc renamed to How It Evolved / When It Stays Lossless / What's Next (site title + TOC) |
| 2 | Intro is unclear about what the learner practically gets | I think this intro is a little short on practically what we're actually doing here / what I'm getting out of it. Like I'm actually getting a walkthru of spec decoding techniques over time | ✅ Made it very explicit about what the learner gets: Introduction → Why it matters, closing paragraph ("By the end, you will have walked through...") |
| 3 | Opener paragraph asks "What does lossless acceleration mean for an LLM?" and never answers it in that paragraph | > start a paragraph literally with "What does lossless acceleration mean for an LLM? " > doesn't even answer it in that paragraph? ... bruh | ✅ Done 9/4: Introduction → How it works, first paragraph now opens "To give you a quick example: serving Qwen3-8B..." |

## Hands-on lab

| # | Feedback | His words | Status |
|---|---|---|---|
| 4 | Show vanilla baseline speed for readers who don't run the lab | For those that don't run I think u can output speed of vanilla for context of those following along | ✅ lab/lab_walkthrough.ipynb Stage 1 embeds every measured result (vanilla 136.3 tok/s, DSpark 231.4, 1.70x) |
| 5 | Lab needs a guided write-up / coding-agent walkthrough, not blind script-running | it could have more written up / guided / full walkthru with your fav coding agent (paste __ into cc / codex / etc) ... w/o the write up it may get lost where people are just blindly running some scripts and seeing number outputs w/o really getting whats happening | ✅ lab/lab_walkthrough.ipynb added: 4-stage guided walkthrough with embedded outputs and teaching questions. ⬜ Optional: coding-agent SKILL.md variant |

## Section 3

| # | Feedback | His words | Status |
|---|---|---|---|
| 6 | 3.1/3.2 are deep for an intro workshop, but acceptable | If this is an intro workshop as u listed it section 3.1 and 3.2 are kinda out there too ... I think it's okay, similar to 3.1 and 3.2 | ✅ No action needed: he judged it acceptable himself |
| 7 | Rename "What's next" to something about how things work today (labs shipping quants etc.) | Maybe rename it form what's next to something around how things actually work today and flowing in labs shipping quants and stuff ties in | ✅ Considered, keeping What's Next: Section 3 content is forward-looking (multimodal, tool-call speculation) |

## Theory

| # | Feedback | His words | Status |
|---|---|---|---|
| 8 | Lossless is defined as a proxy of acceptance rate too much; acceptance rate is an efficiency metric | I think you define lossless as a proxy of acceptance rate a bit too much whereas I'd expect acceptance rate to be used for an efficiency metric | ✅ Fixed 9/4 (same issue Andrew raised): Theorem 3.5 passage rewritten (Introduction → How it works, last paragraph before the summary) — losslessness follows from the algorithm; τ reads as a speed statement, affects quality only when the acceptance threshold is relaxed. Also created an interactive demo of the acceptance threshold affecting speed and quality: Section 2.4, Figure 14 |

---

## Raw transcript (verbatim, in order)

> Hihi sorry super busy day
> Will look at it tonight
> Will leave comments on Google Docs / notes here
> ok I'm going thru interactive first

> This is a lot of saying "what lossless means"
>
> \> start a paragraph literally with "What does lossless acceleration mean for an LLM? "
>
> \> doesn't even answer it in that paragraph?

> bruh

> Also idk I think this content is fine but like why are we spending so much time defining lossless?

> Like from a teaching / learning perspective - yes I want people to question this technique and be like but wait, whats the catch, how are we just more than 2xing out speed? Is there a catch? Do we suffer on quality?
>
> \> no, is lossless meaning __ > ok move on

> Yes it's critical, etc and I think most of this content is fine but the angle seems to keep focus on this term a bit too much imo?

> I think this intro is a little short on practically what we're actually doing here / what I'm getting out of it

> Like I'm actually getting a walkthru of spec decoding techniques over time

> For those that don't run I think u can output speed of vanilla for context of those following along

> Hands on lab seems cool, I think it could have more written up / guided / full walkthru with your fav coding agent (paste __ into cc / codex / etc) and it walks u thru whats happening

> I think w/o the write up it may get lost where people are just blindly running some scripts and seeing number outputs w/o really getting whats happening / why / seeing where something is implemented

> If this is an intro workshop as u listed it section 3.1 and 3.2 are kinda out there too

> I think it's okay, similar to 3.1 and 3.2

> Maybe rename it form what's next to something around how things actually work today and flowing in labs shipping quants and stuff ties in

> Hmm also I think you define lossless as a proxy of acceptance rate a bit too much whereas I'd expect acceptance rate to be used for an efficiency metric
