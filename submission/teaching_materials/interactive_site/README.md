# Interactive Site

The interactive article. **Edit the markdown, never the HTML.**

```
sections/         # source of truth — edit these
  00_lede.md       
  01_introduction.md
  02_whats_measured.md
  03_whats_missed.md
  04_whats_next.md
  05_hands_on_lab.md
template.html     # page shell: CSS, title block, scripts. Edit only for design changes.
build.py          # sections → pandoc → index.html (regenerates TOC, copies the figure in)
index.html        # COMPILED OUTPUT
teaser_figure.png
```

## Workflow

```bash
# 1. edit sections/03_whats_missed.md
# 2. rebuild + open in browser — one command:
./build.sh
```

(`build.sh` checks pandoc is installed, runs `build.py`, and opens `index.html`.)
