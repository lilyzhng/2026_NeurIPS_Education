#!/usr/bin/env python3
"""Build index.html from sections/*.md.

- template.html provides the full page shell (CSS, header, TOC placeholder, scripts)
- sections/00_lede.md          -> rendered into <div class="lede">
- sections/01..05_*.md         -> concatenated article body (raw HTML blocks pass through)
- TOC is regenerated from the <div id="..."> markers + headings in the sections
- ../../figures/teaser_figure.png is copied into figures/ (self-contained for the ZIP)

Usage: python3 build.py
"""
import re, subprocess, os, shutil, glob

HERE = os.path.dirname(os.path.abspath(__file__))

def pandoc(md):
    # protect whole MathJax blocks — gfm would strip backslashes and read _ as emphasis
    kept = []
    def stash(m):
        kept.append(m.group(0))
        return f'MATHJAXBLOCK{len(kept)-1}ENDMATHJAX'
    md = re.sub(r'\\\[.*?\\\]', stash, md, flags=re.S)
    md = re.sub(r'\\\(.*?\\\)', stash, md)
    out = subprocess.run(
        ['pandoc', '-f', 'gfm', '-t', 'html', '--wrap=none'],
        input=md, capture_output=True, text=True, check=True).stdout
    for i, block in enumerate(kept):
        out = out.replace(f'MATHJAXBLOCK{i}ENDMATHJAX', block)
    return out

tpl = open(os.path.join(HERE, 'template.html')).read()

sections = sorted(glob.glob(os.path.join(HERE, 'sections', '*.md')))
lede_file = [s for s in sections if s.endswith('00_lede.md')]
body_files = [s for s in sections if not s.endswith('00_lede.md')]

# --- lede ---
lede_html = ''
if lede_file:
    lede_html = '<div class="lede">\n' + pandoc(open(lede_file[0]).read()) + '\n</div>'

# --- body ---
body_html = '\n'.join(pandoc(open(f).read()) for f in body_files)
content = lede_html + '\n' + body_html

# --- TOC: pair each <div id="X"> with the heading that follows it ---
toc_items = []
for m in re.finditer(r'<div id="([^"]+)" class="section">\s*\n*\s*<h([23])[^>]*>(.*?)</h\2>', body_html, re.S):
    sid, level, text = m.group(1), m.group(2), re.sub(r'<[^>]+>', '', m.group(3)).strip()
    cls = ' class="sub"' if level == '3' else ''
    toc_items.append(f'      <li{cls}><a href="#{sid}">{text}</a></li>')
toc = '\n'.join(toc_items)

out = tpl.replace('<!--TOC-->', toc).replace('<!--CONTENT-->', content)
open(os.path.join(HERE, 'index.html'), 'w').write(out)

# --- figures next to the html so the site is self-contained ---
fig = os.path.join(HERE, '..', '..', 'figures', 'teaser_figure.png')
if os.path.exists(fig):
    os.makedirs(os.path.join(HERE, 'figures'), exist_ok=True)
    shutil.copy(fig, os.path.join(HERE, 'figures', 'teaser_figure.png'))

print(f'built index.html ({len(out)} bytes), {len(toc_items)} TOC entries')
