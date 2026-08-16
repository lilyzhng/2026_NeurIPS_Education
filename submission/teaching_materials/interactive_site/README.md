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
# 1. edit sections/03_whats_missed.md (or any section)
# 2. rebuild
python3 build.py
# 3. open index.html to check
```

Notes:

- Requires pandoc (`brew install pandoc`).
- Section files may contain raw HTML blocks (`<figure>`, `<div class="tbd">`) — they pass through verbatim.
- MathJax delimiters (`\(` `\[`) are protected by build.py; write math normally.
- The TOC on the left is regenerated from the `<div id="...">` markers + headings in each section — keep the `<div id="x" class="section">` wrapper lines intact when editing.
