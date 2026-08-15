# NeurIPS 2026 Education Track — Is Speculative Decoding All We Need?

Submission for the [NeurIPS 2026 Call for Educational Resources](https://neurips.cc/Conferences/2026/CallforEducationalResources).

- **Deadline:** 4 September 2026 (submit via [OpenReview](https://openreview.net/group?id=NeurIPS.cc/2026/Education_Track))
- **Notification:** 28 September 2026
- **Conference:** Sydney, Australia
- **Collaborators:** Lily Zhang + Madison Kanna

## Folder structure

```
├── submission/     # EVERYTHING that goes to OpenReview lives here
│   ├── paper/              # the 2-page PDF statement (LaTeX source + compiled PDF)
│   ├── interactive_site/   # interactive website — self-contained index.html (P1 artifact, in progress)
│   ├── figures/            # our original figures (shared by paper + interactive_site)
│   ├── video/              # video content (scripts, recordings) — recording TBD
│   └── Openreview_Form.md # every OpenReview form field, ready to copy-paste
└── guidelines/     # the scraped CFP — the requirements contract
```

**Teaching materials do not exist yet.** Prior materials (AIE poster/article/script) can't be submitted — the CFP requires materials created specifically for this track. New materials get built fresh inside `submission/` and zipped before the Sept 4 deadline.

## Build

```bash
# 2-page PDF
cd submission/paper && pdflatex submission.tex

# Teaching-materials ZIP (must stay under 200MB) — once the materials exist:
# cd submission && zip -r ../education-materials.zip interactive_site video <materials> -x '*/.claude/*' '*/.DS_Store'
# (paper/ is uploaded separately — it does not go in the ZIP)
```

## Open tasks (from 8/15 sync)

- [ ] Lily: push content to GitHub, invite Madison as co-contributor
- [ ] Madison: create OpenReview account
- [ ] Madison: label all questions so they're relatable for a technical audience without speculative-decoding expertise
- [ ] Pick section of interest to develop artifacts; recording later
- [ ] Interactive website to convey ideas (P1)
- [ ] Expert for "what's next" section — candidates: Zhijian Liu, Eugine, Featherless (P2)
- [ ] Next sync: Monday 8/17, 2:30 PM

## Inspiration (accepted exemplars)

- [The Art of Picking the Next Token](https://sampling.amanvir.com/) — NeurIPS 2025 Education, interactive scrollytelling teaching sampling. Closest exemplar to ours.
- [The Science of Benchmarking](https://benchmarking.science/) — NeurIPS 2025 tutorial; our article borrows its What's Measured / What's Missed / What's Next framing.
- [NeurIPS 2025 Education Program](https://openreview.net/group?id=NeurIPS.cc/2025/Education_Program#tab-accept) — full list of what got in last year.

## Submission requirements (from the CFP)

- 2-page PDF: concept, leveling/prerequisites, learning objectives, ≥3 linked papers (2022–2026), teaching-materials summary
- Teaching materials as ZIP under 200MB; all content **original, created for this track**
- Single-blind: author names included
