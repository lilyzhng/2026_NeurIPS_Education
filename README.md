# [NeurIPS 2026 Education Track] Speculative Decoding: What Lossless Means, What It Doesn't, and What's Next

- **Deadline:** 4 September 2026 (submit via [OpenReview](https://openreview.net/group?id=NeurIPS.cc/2026/Education_Track))
- **Notification:** 28 September 2026
- **Conference:** Sydney, Australia
- **Collaborators:** Lily Zhang + Madison Kanna

## Folder structure

```
├── submission/   
│   ├── 2_page_pdf/       
│   ├── teaching_materials/ 
│   │   ├── interactive_site/  
│   │   └── video/           
│   ├── figures/          
│   └── Openreview_Form.md
```

## Build

```bash
# 2-page PDF
cd submission/2_page_pdf && pdflatex submission.tex
```

## Inspiration (accepted examples)

- [The Art of Picking the Next Token](https://sampling.amanvir.com/) — NeurIPS 2025 Education, interactive scrollytelling teaching sampling. Closest exemplar to ours.
- [The Science of Benchmarking](https://benchmarking.science/) — NeurIPS 2025 tutorial; our article borrows its What's Measured / What's Missed / What's Next framing.
- [NeurIPS 2025 Education Program](https://openreview.net/group?id=NeurIPS.cc/2025/Education_Program#tab-accept) — full list of what got in last year.

## Neurips CFP Submission requirements

Source: [neurips.cc/Conferences/2026/CallforEducationalResources](https://neurips.cc/Conferences/2026/CallforEducationalResources).

### About the track

The Education Track will feature keynote talks from leading AI educators. Accepted submissions will be presented as short presentations on the latest technical concepts, as well as poster sessions for deeper in-person discussions. The track has two goals: to create stand-alone educational resources, and to ensure that emerging concepts are taught clearly as entry points into the main conference.

**Who should attend?** The intended audience for the educational material that are presented includes:

- First-time NeurIPS attendees, young researchers or anyone new to AI;
- Educators who need to keep curricula current, and who can reuse or reshape the track's materials for their own introductory or advanced courses;
- Lecturers and research groups who want to teach (or learn!) with clear and self-contained examples;
- Non-specialists for whom the core ideas at NeurIPS are otherwise hidden behind specialist terminology.

By the end of the day, track attendees will walk away with:

- A working grasp of emerging technical concepts, sufficient to follow talks and posters that build on these concepts throughout the NeurIPS week;
- Reusable learning materials, which pair each concept with learning artifacts (e.g., code notebooks, videos, slides) that learners can take away and keep using long after the conference.

### Call for submissions

**Who can submit?** We're looking for researchers and educators with a strong command of an emerging concept and the ability to teach it to a broad audience. Submitters and content creators do not need to be the original author of the idea; what matters is that they can teach the essence and technical nuances of a concept in an engaging way. We welcome contributions from individuals and organizations, including students, nonprofits, outreach teams, researchers and educators at all levels.

**What is a concept?** A concept is a technical advancement or technique that has emerged in AI research over the past few years and is shaping work across the field today, including papers at NeurIPS 2026. Think of recent equivalents of ideas like the "reparameterization trick". It can also be an older idea that has resurfaced or taken on a new form within the last few years. Note, submissions on *introductions* to well-established knowledge (e.g. backpropagation, transformers, or variational inference) will not be considered. The track seeks to explain the newer concepts that researchers are reaching for right now.

**What does a submission look like?** We welcome submissions in a variety of formats, including (but not limited to):

- Illustrative code, code libraries and IPython notebooks that serve to teach an emerging AI concept, trend, or even "training tricks";
- Short videos, including lightboard videos, that explain an AI concept;
- Lecture notes and slide decks, designed for learners with a specific stated background;
- Interactive demos or notebooks that help learners explore AI concepts intuitively;
- Visual explanations with infographics, animations, or accessible illustrations of AI tools and techniques.

Submissions could combine a number of formats to teach an emerging theme in a clear way, and may include exercises for learners. An example submission might be a visual, interactive breakdown of "Direct Preference Optimization (DPO)" that is supported by an IPython notebook and accompanying slides, lightboard videos or exercises. Submissions need to be as self-contained as possible, and should include a copy of source code even if the "ground truth" is hosted on a public repository. Resources that are created for the submission that *individually* exceed ~40MB in size may be hosted at a permanent external URL and referenced in the submission; these would typically be example datasets that are used, videos, pretrained model weights, etc. Submissions should state their prerequisite knowledge, as well as the learning objectives of the submission. **All educational resources must be original and specifically created for the NeurIPS 2026 Education Track.**

### How to submit

All submissions to the NeurIPS 2026 Education Track must include:

- A PDF of not more than two pages (please use the "education, final" [paper template](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip) without the checklist for consistent formatting), summarizing:
  - *The concept:* A short summary of the concept that is being taught.
  - *Leveling and prerequisite knowledge:* What level of technical knowledge is required to understand the material? Would the material be suitable at the level of pre-university, 1st year university, advanced undergraduate or graduate teaching?
  - *Learning objectives and outcomes:* A clear, specific statement of what a learner will achieve by the end of the material. This can include descriptions of things a learner will remember, understand, apply, analyse, evaluate or create, stated at different levels of engagement, from remembering facts to creating original work.
  - *Linked papers:* At least three recent papers from NeurIPS and its sister conferences or other leading venues in 2022–2026 (or widely-cited recent arXiv work) that use this concept, demonstrating it is in active use at the frontier.
  - *Teaching materials summary:* A summary of the artifacts provided to teach the concept.
- Teaching materials that will be used to teach the AI concept. The material must be submitted as a ZIP file under 200MB in size, and may link to a public code repository and links to accompanying explanatory videos. All educational resources must be original and specifically created for the 2026 Education Track.

Submissions must be uploaded through OpenReview here: [NeurIPS.cc/2026/Education_Track](https://openreview.net/group?id=NeurIPS.cc/2026/Education_Track).

### Important dates

- 3 July 2026: Submissions open
- 4 September 2026: Submissions close
- 28 September 2026: Notification of acceptance

### Single-blind review policy

The names of the authors should be included in the submission.

### Selected submissions

Accepted submissions will:

- Be invited to present either a **talk** or a **poster** on the emerging concept, showcasing the educational material and teaching the concept. Presentations may be accompanied by interactive demonstrations or presentations on display screens;
- Be made available for download via the NeurIPS website (non-archival format);
- Be curated into an official NeurIPS 2026 Education Track repository;
- Be eligible for the People's Choice Award, selected by attendee votes during the event.

### Conference and presentation policy

For this track, the presentations will take place only at the main conference site in Sydney, Australia. If a work is accepted, at least one author must register for the conference to attend it in person. For registration policy and registration fee information, visit [NeurIPS 2026](https://neurips.cc/Conferences/2026).

### Contact

For questions regarding submission or content guidelines, please contact the NeurIPS 2026 Education Chairs at education-chairs@neurips.cc.
