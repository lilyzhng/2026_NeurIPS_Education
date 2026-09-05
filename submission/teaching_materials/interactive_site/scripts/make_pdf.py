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

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
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
    png = os.path.join(OUT_DIR, name + '.png')
    url = 'file://' + os.path.join(HERE, src) + '?final=1'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu',
                    f'--window-size={WIDTH},{OVERSHOOT}',
                    '--force-device-scale-factor=2', '--hide-scrollbars',
                    f'--virtual-time-budget={budget}',
                    f'--screenshot={png}', url],
                   check=True, capture_output=True)
    trim(png)
    print('shot:', name, Image.open(png).size)
    return png


# 1. figures
shots = {}
for f in sorted(glob.glob(os.path.join(HERE, 'figures', '*_chalk.html'))):
    name = os.path.basename(f)[:-5]
    shots['figures/' + os.path.basename(f)] = 'figures/print/' + name + '.png'
    shoot(os.path.join('figures', os.path.basename(f)), name)
shots['demo/knob_demo.html'] = 'figures/print/knob_demo.png'
shoot(os.path.join('demo', 'knob_demo.html'), 'knob_demo', budget=8000)

# 2. print.html: swap iframes for imgs
html = open(os.path.join(HERE, 'index.html')).read()
def sub(m):
    src = m.group(1)
    key = src.lstrip('./')
    if key in shots:
        return f'<img src="{shots[key]}" style="width:100%;" alt="figure (static render)">'
    return m.group(0)
html = re.sub(r'<iframe src="([^"]+)"[^>]*></iframe>', sub, html)
open(os.path.join(HERE, 'print.html'), 'w').write(html)

# 3. PDF
pdf = os.path.abspath(os.path.join(HERE, '..', 'pdf', 'teaching_writeup.pdf'))
subprocess.run([CHROME, '--headless=new', '--disable-gpu',
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
