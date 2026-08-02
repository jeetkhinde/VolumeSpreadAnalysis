"""Extract per-page lines with geometry + font size from the PDF."""
import json
import pypdfium2 as pdfium

import paths as cfg


def page_lines(page):
    """Return list of {text, top, bottom, left, right, size} in reading order."""
    tp = page.get_textpage()
    n = tp.count_chars()
    chars = []
    for i in range(n):
        try:
            box = tp.get_charbox(i)  # (left, bottom, right, top)
        except Exception:
            continue
        if box is None:
            continue
        ch = tp.get_text_range(i, 1)
        if ch == '\r':
            continue
        chars.append((ch, box))

    lines = []
    cur = []
    for ch, box in chars:
        if ch == '\n':
            if cur:
                lines.append(cur)
                cur = []
            continue
        cur.append((ch, box))
    if cur:
        lines.append(cur)

    out = []
    for ln in lines:
        text = ''.join(c for c, _ in ln)
        if not text.strip():
            continue
        boxes = [b for c, b in ln if c.strip()]
        if not boxes:
            continue
        left = min(b[0] for b in boxes)
        bottom = min(b[1] for b in boxes)
        right = max(b[2] for b in boxes)
        top = max(b[3] for b in boxes)
        # glyph height as font-size proxy; use median to resist outliers
        hs = sorted(b[3] - b[1] for b in boxes)
        size = hs[len(hs) // 2]
        out.append({
            'text': text.rstrip(),
            'top': round(top, 2),
            'bottom': round(bottom, 2),
            'left': round(left, 2),
            'right': round(right, 2),
            'size': round(size, 2),
        })
    out.sort(key=lambda d: -d['top'])
    return out


def main():
    pdf = pdfium.PdfDocument(cfg.PDF)
    allpages = []
    for i in range(len(pdf)):
        page = pdf[i]
        w, h = page.get_size()
        lines = page_lines(page)
        images = []
        for obj in page.get_objects():
            if obj.type == 3:  # image
                try:
                    images.append([round(v, 2) for v in obj.get_bounds()])
                except Exception:
                    pass
        paths = []
        for obj in page.get_objects():
            if obj.type == 2:  # path (annotation arrows/boxes)
                try:
                    paths.append([round(v, 2) for v in obj.get_bounds()])
                except Exception:
                    pass
        allpages.append({
            'pdf_page': i + 1,
            'width': w, 'height': h,
            'lines': lines,
            'images': images,
            'paths': paths,
        })
        if (i + 1) % 25 == 0:
            print('...', i + 1)
    json.dump(allpages, open(cfg.LINES_JSON, 'w'))
    print('wrote lines.json for', len(allpages), 'pages')


if __name__ == '__main__':
    main()
