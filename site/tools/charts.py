"""Render chart figures from the PDF, preserving vector annotation overlays."""
import json
import os
import re
import sys

import pypdfium2 as pdfium

LINES = json.load(open('lines.json'))

PDF = 'Master the Markets by Tom Williams.pdf'
SCALE = 3.0          # ~216 DPI
MIN_W = 120          # ignore decorative glyph images (PDF points)
MIN_H = 60
PAD = 3.0


def intersects(a, b, slack=6.0):
    al, ab, ar, at = a
    bl, bb, br, bt = b
    return not (ar + slack < bl or br + slack < al or at + slack < bb or bt + slack < ab)


def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def cluster(boxes):
    """Merge overlapping/adjacent image boxes into figure clusters."""
    boxes = [list(b) for b in boxes]
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                if intersects(boxes[i], boxes[j], slack=10.0):
                    boxes[i] = union(boxes[i], boxes[j])
                    boxes.pop(j)
                    merged = True
                    break
            if merged:
                break
    return boxes


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    pdf = pdfium.PdfDocument(PDF)
    meta = []
    for i in range(len(pdf)):
        pdfpage = i + 1
        page = pdf[i]
        W, H = page.get_size()
        imgs, paths = [], []
        for obj in page.get_objects():
            try:
                b = list(obj.get_bounds())
            except Exception:
                continue
            if obj.type == 3:
                imgs.append(b)
            elif obj.type == 2:
                paths.append(b)
        imgs = [b for b in imgs if (b[2] - b[0]) >= MIN_W and (b[3] - b[1]) >= MIN_H]
        if not imgs:
            continue
        figs = cluster(imgs)
        # grow each figure to include annotation paths drawn over/around it
        for k, f in enumerate(figs):
            grew = True
            while grew:
                grew = False
                for p in paths:
                    pw, ph = p[2] - p[0], p[3] - p[1]
                    if pw > W * 0.95 or ph > H * 0.95:
                        continue  # page border/rule, not an annotation
                    if intersects(f, p) and not (
                        p[0] >= f[0] and p[1] >= f[1] and p[2] <= f[2] and p[3] <= f[3]
                    ):
                        nf = union(f, p)
                        if nf != f:
                            f = nf
                            grew = True
                figs[k] = f
        # Pad first, then clamp against neighbouring body text so captions/
        # headings never bleed into the figure.
        plines = LINES[i]['lines']
        padded = []
        for f in figs:
            l = max(0, f[0] - PAD); b = max(0, f[1] - PAD)
            r = min(W, f[2] + PAD); t = min(H, f[3] + PAD)
            below = [ln for ln in plines if ln['top'] <= f[1] + 1 and ln['size'] < 15]
            above = [ln for ln in plines if ln['bottom'] >= f[3] - 1 and ln['size'] < 15]
            if below:
                nearest = max(below, key=lambda ln: ln['top'])
                b = max(b, nearest['top'] + 2.0)
            if above:
                nearest = min(above, key=lambda ln: ln['bottom'])
                t = min(t, nearest['bottom'] - 2.0)
            padded.append((l, b, r, t))

        bitmap = page.render(scale=SCALE).to_pil()
        for k, (l, b, r, t) in enumerate(padded):
            box = (int(l * SCALE), int((H - t) * SCALE), int(r * SCALE), int((H - b) * SCALE))
            crop = bitmap.crop(box)
            name = f'p{pdfpage:03d}_{k}.png'
            crop.save(os.path.join(outdir, name), optimize=True)
            meta.append({
                'file': name, 'pdf_page': pdfpage, 'idx': k,
                'bounds': [round(l, 1), round(b, 1), round(r, 1), round(t, 1)],
                'px': list(crop.size),
            })
        if pdfpage % 25 == 0:
            print('...', pdfpage, file=sys.stderr)
    json.dump(meta, open('charts.json', 'w'), indent=1)
    print('rendered', len(meta), 'figures')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'figs')
