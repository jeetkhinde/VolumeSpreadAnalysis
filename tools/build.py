"""Turn the extracted lines + figures into MDX chapters and a glossary dataset.

Figures are placed by their position on the page (not by caption matching), so
uncaptioned illustrations survive. A caption line immediately following a figure
is absorbed into it.
"""
import json
import os
import re
import shutil
import unicodedata

import paths as cfg
import toc
from PIL import Image

LINES = json.load(open(cfg.LINES_JSON))
CHARTS = json.load(open(cfg.CHARTS_JSON))

OUT = cfg.CONTENT
FIGS_OUT = cfg.FIGS_OUT
WEBP_QUALITY = 90

FOOTER = re.compile(r'^\s*Master the Markets\s+\d+\s*$')
CAPTION = re.compile(r'^\s*(Chart\s+\d+[a-z]?)\s*[:\.]?\s*(.*)$', re.I)
BULLET = re.compile(r'^\s*[•]\s*')
NUMBERED = re.compile(r'^\s*(\d{1,2})[\.\)]\s+')
PARA_GAP = 16.0     # PDF points; body line pitch is ~11.5
HEAD_SIZE = 15.0    # chapter/section titles
TERM_SIZE = 9.0     # glossary terms

figs_by_page = {}
for c in CHARTS:
    figs_by_page.setdefault(c['pdf_page'], []).append(c)
for v in figs_by_page.values():
    v.sort(key=lambda c: -c['bounds'][3])


def slugify(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('&', ' and ')
    s = re.sub(r"[’'‘]", '', s)
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return re.sub(r'-{2,}', '-', s)


def clean(t):
    t = t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()


def join_lines(parts):
    out = ''
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if not out:
            out = p
        elif out.endswith('-'):
            out += p
        else:
            out += ' ' + p
    return clean(out)


def page_items(pdfpage, keep_headings=False):
    """Ordered page contents: text lines and figures interleaved top-to-bottom."""
    rec = LINES[pdfpage - 1]
    items = []
    for l in rec['lines']:
        if FOOTER.match(l['text']) or not l['text'].strip():
            continue
        if not keep_headings and l['size'] >= HEAD_SIZE:
            continue
        items.append({'kind': 'line', 'y': l['top'], 'l': l})
    for f in figs_by_page.get(pdfpage, []):
        items.append({'kind': 'fig', 'y': f['bounds'][3], 'f': f})
    items.sort(key=lambda d: -d['y'])
    return items


def blocks_for_pages(pages):
    """Build semantic blocks across a run of pages."""
    blocks = []
    cur = None
    prev = None
    for pdfpage in pages:
        items = page_items(pdfpage)
        i = 0
        while i < len(items):
            it = items[i]
            if it['kind'] == 'fig':
                cur = None
                prev = None
                cap_label, cap_text = None, None
                if i + 1 < len(items) and items[i + 1]['kind'] == 'line':
                    nxt = items[i + 1]['l']['text']
                    m = CAPTION.match(nxt)
                    if m:
                        cap_label, cap_text = m.group(1), m.group(2)
                        i += 1
                blocks.append({'t': 'figure', 'src': '/figures/' + it['f']['file'].replace('.png', '.webp'),
                               'w': it['f']['px'][0], 'h': it['f']['px'][1],
                               'label': cap_label, 'caption': cap_text})
                i += 1
                continue

            l = it['l']
            txt = l['text']
            gap = (prev['top'] - l['top']) if prev else 999.0
            is_sub = TERM_SIZE <= l['size'] < HEAD_SIZE
            is_bullet = bool(BULLET.match(txt))
            is_num = bool(NUMBERED.match(txt)) and l['left'] < 130

            if is_sub:
                blocks.append({'t': 'subhead', 'text': clean(txt)})
                cur = None
            elif is_bullet:
                cur = {'t': 'bullet', 'text': clean(BULLET.sub('', txt))}
                blocks.append(cur)
            elif is_num:
                cur = {'t': 'number', 'text': clean(txt)}
                blocks.append(cur)
            elif gap > PARA_GAP or cur is None:
                cur = {'t': 'para', 'text': clean(txt)}
                blocks.append(cur)
            else:
                cur['text'] = join_lines([cur['text'], txt])
            prev = l
            i += 1
    return blocks


def merge_page_breaks(blocks):
    """Rejoin a paragraph/list item split across a page boundary."""
    out = []
    for b in blocks:
        if (out and b['t'] == 'para' and out[-1]['t'] in ('para', 'bullet', 'number')
                and out[-1]['text'] and out[-1]['text'][-1] not in '.:;!?”"'
                and b['text'] and b['text'][0].islower()):
            out[-1]['text'] = join_lines([out[-1]['text'], b['text']])
        else:
            out.append(b)
    return out


def to_mdx(blocks):
    md = []
    for b in blocks:
        if b['t'] == 'figure':
            attrs = f'src="{b["src"]}" width={{{b["w"]}}} height={{{b["h"]}}}'
            if b['label']:
                attrs += f' label={json.dumps(b["label"])}'
            if b['caption']:
                attrs += f' caption={json.dumps(b["caption"], ensure_ascii=False)}'
            md.append(f'<Figure {attrs} />')
        elif b['t'] == 'subhead':
            md.append(f'### {b["text"]}')
        elif b['t'] == 'bullet':
            md.append(f'- {b["text"]}')
        else:
            md.append(b['text'])
    return '\n\n'.join(md)


def collect_glossary():
    entries = []
    cur = None
    for p in range(142, 181):
        pdfpage = toc.printed_to_pdf(p)
        items = page_items(pdfpage, keep_headings=True)
        prev = None
        i = 0
        while i < len(items):
            it = items[i]
            if it['kind'] == 'fig':
                if cur is not None:
                    cap_label, cap_text = None, None
                    if i + 1 < len(items) and items[i + 1]['kind'] == 'line':
                        m = CAPTION.match(items[i + 1]['l']['text'])
                        if m:
                            cap_label, cap_text = m.group(1), m.group(2)
                            i += 1
                    cur['blocks'].append({'t': 'figure', 'src': '/figures/' + it['f']['file'].replace('.png', '.webp'),
                                          'w': it['f']['px'][0], 'h': it['f']['px'][1],
                                          'label': cap_label, 'caption': cap_text})
                prev = None
                i += 1
                continue
            l = it['l']
            txt = l['text']
            if TERM_SIZE <= l['size'] < HEAD_SIZE:
                cur = {'term': clean(txt), 'blocks': [], 'page': p}
                entries.append(cur)
                prev = None
                i += 1
                continue
            if l['size'] >= HEAD_SIZE or cur is None:
                i += 1
                continue
            gap = (prev['top'] - l['top']) if prev else 999.0
            if BULLET.match(txt):
                cur['blocks'].append({'t': 'bullet', 'text': clean(BULLET.sub('', txt))})
            elif (gap > PARA_GAP or not cur['blocks']
                  or cur['blocks'][-1]['t'] != 'para'):
                cur['blocks'].append({'t': 'para', 'text': clean(txt)})
            else:
                cur['blocks'][-1]['text'] = join_lines([cur['blocks'][-1]['text'], txt])
            prev = l
            i += 1
    for e in entries:
        e['slug'] = slugify(e['term'])
    return [e for e in entries if e['blocks']]


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(f'{OUT}/book', exist_ok=True)
    if os.path.exists(FIGS_OUT):
        shutil.rmtree(FIGS_OUT)
    os.makedirs(FIGS_OUT, exist_ok=True)

    manifest = []
    order = 0

    def emit(title, section, start, end):
        nonlocal order
        order += 1
        pages = [toc.printed_to_pdf(p) for p in range(start, end + 1)]
        blocks = merge_page_breaks(blocks_for_pages(pages))
        body = to_mdx(blocks)
        slug = slugify(title)
        fm = {'title': title, 'section': section, 'order': order,
              'printedStart': start, 'printedEnd': end,
              'figures': body.count('<Figure')}
        front = '---\n' + '\n'.join(
            f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in fm.items()
        ) + '\n---\n\n'
        open(f'{OUT}/book/{order:03d}-{slug}.mdx', 'w').write(front + body + '\n')
        manifest.append({**fm, 'slug': slug, 'words': len(body.split())})

    emit('Preamble', 'Front Matter', 8, 8)
    emit('Introduction', 'Front Matter', 9, 10)
    for sec_title, divider, topics, sec_end in toc.SECTIONS:
        for i, (t, start) in enumerate(topics):
            end = topics[i + 1][1] - 1 if i + 1 < len(topics) else sec_end
            emit(t, sec_title, start, end)
    for title, s, e in toc.APPENDIX:
        emit(title, 'Appendix', s, e)

    data_dir = os.path.join(cfg.SITE, 'src', 'data')
    os.makedirs(data_dir, exist_ok=True)
    gl = collect_glossary()
    json.dump(gl, open(f'{data_dir}/glossary.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(manifest, open(f'{data_dir}/manifest.json', 'w'), ensure_ascii=False, indent=1)

    used = set()
    for f in sorted(os.listdir(f'{OUT}/book')):
        used |= set(re.findall(r'/figures/(\S+?\.webp)', open(f'{OUT}/book/{f}').read()))
    used |= {b['src'].split('/')[-1] for e in gl for b in e['blocks'] if b['t'] == 'figure'}
    for name in sorted(used):
        src = os.path.join(cfg.FIGS_RAW, name.replace('.webp', '.png'))
        im = Image.open(src).convert('RGB')
        im.save(os.path.join(FIGS_OUT, name), quality=WEBP_QUALITY, method=6)

    print(f'chapters : {len(manifest)}')
    print(f'words    : {sum(m["words"] for m in manifest):,}')
    print(f'figures  : {sum(m["figures"] for m in manifest)} in chapters, '
          f'{sum(1 for e in gl for b in e["blocks"] if b["t"] == "figure")} in glossary, '
          f'{len(used)} copied')
    print(f'glossary : {len(gl)} terms')


if __name__ == '__main__':
    main()
