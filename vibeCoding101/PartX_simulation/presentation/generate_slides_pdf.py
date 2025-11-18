#!/usr/bin/env python3
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from pathlib import Path

P = Path(__file__).resolve().parent
TRANSCRIPT = P / 'Part3_full_transcript_en.txt'
OUT = P / 'Part3_slides_1-12_presentation.pdf'

if not TRANSCRIPT.exists():
    raise SystemExit('Transcript not found: ' + str(TRANSCRIPT))

# Read transcript and split slides
with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
    text = f.read()

slides = []
blocks = text.split('\n\n')
# We'll parse using known headings 'Slide X —'
current = None
for line in text.splitlines():
    if line.startswith('Slide') and '—' in line:
        # start new
        if current:
            slides.append(current)
        current = {'title': line.strip(), 'notes': ''}
    elif current is not None:
        current['notes'] += line + '\n'
if current:
    slides.append(current)

# Keep first 12 slides
slides = slides[:12]

# Create PDF
c = canvas.Canvas(str(OUT), pagesize=landscape(A4))
width, height = landscape(A4)

for s in slides:
    # Title
    c.setFont('Helvetica-Bold', 20)
    c.drawString(20*mm, height - 20*mm, s['title'])
    # Notes body
    c.setFont('Helvetica', 12)
    textobject = c.beginText()
    textobject.setTextOrigin(20*mm, height - 30*mm)
    textobject.setLeading(14)
    # wrap lines: split by newline already present
    for para in s['notes'].strip().split('\n'):
        # ensure long lines wrap
        max_chars = 120
        while len(para) > max_chars:
            textobject.textLine(para[:max_chars])
            para = para[max_chars:]
        textobject.textLine(para)
        textobject.textLine('')
    c.drawText(textobject)
    c.showPage()

c.save()
print('Wrote', OUT)
