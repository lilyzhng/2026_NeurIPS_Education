# Interactive Site

The interactive article. Edit the markdown, never the HTML.

```
sections/               # source of truth — edit these
  00_introduction.md         # Introduction: Why it matters + How it works
  01_what_lossless_means.md  # 1. How speculative decoding evolved (1.1–1.5)
  02_what_it_doesnt_mean.md  # 2. When it stays lossless (2.1–2.4 Hands-On Lab)
  03_whats_next.md           # 3. What's Next (3.1–3.2)
  04_references.md           # References + citation block
  05_appendix.md             # Appendix (A.1, A.2)
template.html           # page shell: CSS (incl. print styles), TOC, scripts
build.py                # sections → pandoc → index.html (regenerates TOC, copies figures + fonts)
index.html              # COMPILED OUTPUT
figures/                # chalkboard figures (self-hosted PencilPete font, final-frame print hooks)
demo/                   # interactive demos (knob_demo.html = the acceptance-rate demo, Figure 14)
watch_build.py          # auto-rebuild on save (for live preview while editing)
make_pdf.py             # site → ../pdf/teaching_writeup.pdf (final-frame screenshots + page numbers)
```

## Workflow

```bash
# 1. edit a file under sections/
# 2. rebuild:
python3 build.py
# or auto-rebuild on every save while editing:
python3 watch_build.py
```

## PDF snapshot

```bash
python3 make_pdf.py
```

Screenshots every chalk figure at its finished animation state, swaps the
iframes for the images, prints to PDF, and stamps page numbers.
