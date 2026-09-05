#!/usr/bin/env python3
"""Render the site to a PDF with figures as final-frame screenshots.

1. Screenshot every chalk figure (and the knob demo) in headless Chrome at
   its finished animation state (?final query) into figures/print/*.png.
2. Build print.html from index.html with each figure iframe replaced by the
   screenshot <img>.
3. Print print.html to ../pdf/teaching_writeup.pdf.

Usage: python3 make_pdf.py
"""
import glob
import os
import re
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE_DIR = tempfile.mkdtemp(prefix='chrome-pdf-')
OUT_DIR = os.path.join(HERE, 'figures', 'print')
os.makedirs(OUT_DIR, exist_ok=True)

WIDTH = 1100
OVERSHOOT = 2600  # capture tall, trim below


def trim(png):
    im = Image.open(png).convert('RGB')
    bg = im.getpixel((im.width - 1, im.height - 1))
    w, h = im.size
    bottom = h
    for y in range(h - 1, 0, -1):
        row = [im.getpixel((x, y)) for x in range(0, w, 40)]
        if any(abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 24 for p in row):
            bottom = min(h, y + 24)
            break
    im.crop((0, 0, w, bottom)).save(png)


def shoot(src, name, budget=30000):
    import hashlib
    png = os.path.join(OUT_DIR, name + '.png')
    html = os.path.join(HERE, src)
    # reuse cached screenshot when the figure html content is unchanged
    digest = hashlib.md5(open(html, 'rb').read()).hexdigest()
    sidecar = png + '.md5'
    if os.path.exists(png) and os.path.exists(sidecar) and open(sidecar).read().strip() == digest:
        print(f'  cached  {name}.png')
        return png
    url = 'file://' + html + '?final=1'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu',
                    f'--user-data-dir={PROFILE_DIR}',
                    f'--window-size={WIDTH},{OVERSHOOT}',
                    '--force-device-scale-factor=2', '--hide-scrollbars',
                    f'--virtual-time-budget={budget}',
                    f'--screenshot={png}', url],
                   check=True, capture_output=True)
    trim(png)
    open(sidecar, 'w').write(digest)
    print('shot:', name, Image.open(png).size)
    return png


# 1. figures: use existing screenshots in figures/print/ (no Chrome, no re-shooting).
# To refresh a figure image, delete its png (or run scripts/snap_figures.py) first.
shots = {}
index_html = open(os.path.join(HERE, 'index.html')).read()
for rel in set(re.findall(r'<iframe src="((?:figures|demo)/[^"]+\.html)"', index_html)):
    name = os.path.basename(rel)[:-5]
    png = os.path.join(OUT_DIR, name + '.png')
    if os.path.exists(png):
        shots[rel] = 'figures/print/' + name + '.png'
    else:
        print('WARNING: no screenshot for', rel, '- iframe left as-is')

# 2. print.html: swap iframes for imgs
html = open(os.path.join(HERE, 'index.html')).read()
BIG = {'figure1_chalk.png', 'rejection_sampling_chalk-v1.png', 'dflash_flat_cost_chalk-v1.png',
       'dflash_kv_injection_chalk-v1.png', 'figure2_chalk.png', 'dflash_draft_chalk.png', 'figure4_chalk.png',
       'figure5_chalk.png', 'figure6_chalk.png', 'figure7_chalk.png', 'figure8_chalk.png', 'figure9_chalk.png'}
FIT = set()
def sub(m):
    src = m.group(1)
    key = src.lstrip('./')
    if key in shots:
        base = os.path.basename(shots[key])
        cls = 'pbig' if base in BIG else ('pfit' if base in FIT else '')
        return f'<img src="{shots[key]}" class="{cls}" alt="figure (static render)">'
    return m.group(0)
html = re.sub(r'<iframe src="([^"]+)"[^>]*></iframe>', sub, html)
open(os.path.join(HERE, 'print.html'), 'w').write(html)

# 3. PDF
pdf = os.path.abspath(os.path.join(HERE, '..', 'pdf', 'teaching_writeup.pdf'))
subprocess.run([CHROME, '--headless=new', '--disable-gpu',
                    f'--user-data-dir={PROFILE_DIR}',
                '--window-size=1400,1000', '--no-pdf-header-footer',
                '--virtual-time-budget=15000',
                f'--print-to-pdf={pdf}',
                'file://' + os.path.join(HERE, 'print.html')],
               check=True, capture_output=True)
# 4. stamp page numbers bottom-right
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
reader = PdfReader(pdf)
writer = PdfWriter()
for i, page in enumerate(reader.pages, 1):
    w = float(page.mediabox.width); h = float(page.mediabox.height)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFont('Times-Roman', 9)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawRightString(w - 36, 24, str(i))
    c.save()
    buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])
    writer.add_page(page)
with open(pdf, 'wb') as fh:
    writer.write(fh)
print('pdf:', pdf, round(os.path.getsize(pdf) / 1e6, 1), 'MB, pages:', len(reader.pages))
