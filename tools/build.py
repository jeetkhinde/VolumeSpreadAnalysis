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
import prune
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
        para_gap = page_para_gap(items)
        first_on_page = True
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

            # A sub-heading must *start* a block. A line sitting at normal line
            # pitch below its predecessor is a wrapped continuation, even when
            # its glyph metrics look large — parentheses and descenders inflate
            # the median height on short lines. Across a page break the gap is
            # meaningless (it goes negative), so treat the first line of a page
            # as starting a block; merge_page_breaks rejoins real continuations.
            if is_sub and (first_on_page or gap > para_gap):
                cur = {'t': 'subhead', 'text': clean(txt)}
                blocks.append(cur)
            elif is_bullet:
                cur = {'t': 'bullet', 'text': clean(BULLET.sub('', txt))}
                blocks.append(cur)
            elif is_num:
                cur = {'t': 'number', 'text': clean(txt)}
                blocks.append(cur)
            elif gap > para_gap or cur is None:
                cur = {'t': 'para', 'text': clean(txt)}
                blocks.append(cur)
            else:
                cur['text'] = join_lines([cur['text'], txt])
            prev = l
            first_on_page = False
            i += 1
    return merge_wrapped_subheads(blocks)


def page_para_gap(items):
    """Paragraph threshold for one page, from its own body line pitch.

    Leading is not constant across the book (11.5pt in the chapters, 17pt on
    the Trading Facts page), so a fixed threshold either splits wrapped lines
    or glues paragraphs together depending on the page.
    """
    tops = [it['l']['top'] for it in items
            if it['kind'] == 'line' and it['l']['size'] < TERM_SIZE]
    gaps = sorted(a - b for a, b in zip(tops, tops[1:]) if 4 < a - b < 60)
    if not gaps:
        return PARA_GAP
    pitch = gaps[len(gaps) // 2]
    return max(14.0, pitch * 1.45)


def merge_wrapped_subheads(blocks):
    """Join a heading that wrapped onto more than one line.

    Two sub-headings never sit back-to-back in this book — there is always body
    text between them — so consecutive subhead blocks are one wrapped heading.
    """
    out = []
    for b in blocks:
        if b['t'] == 'subhead' and out and out[-1]['t'] == 'subhead':
            out[-1]['text'] = join_lines([out[-1]['text'], b['text']])
        else:
            out.append(b)
    return out


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
    if os.path.exists(f'{OUT}/book'):
        shutil.rmtree(f'{OUT}/book')
    os.makedirs(f'{OUT}/book', exist_ok=True)
    if os.path.exists(FIGS_OUT):
        shutil.rmtree(FIGS_OUT)
    os.makedirs(FIGS_OUT, exist_ok=True)

    manifest = []
    prune_hits = []
    order = 0

    def emit(title, section, start, end):
        nonlocal order
        order += 1
        print(f"Emitting {order} {title} {start} {end}")
        slug = slugify(title)

        if start == 'custom':
            body = open(f'tools/custom/{slug}.mdx').read()
            fm = {'title': title, 'section': section, 'order': order,
                  'printedStart': 120, 'printedEnd': 120,
                  'figures': body.count('<Figure')}
            front = '---\n' + '\n'.join(
                f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in fm.items()
            ) + '\n---\n\n'
            open(f'{OUT}/book/{order:03d}-{slug}.mdx', 'w').write(front + body + '\n')
            manifest.append({**fm, 'slug': slug, 'words': len(body.split())})
            return

        pages = [toc.printed_to_pdf(p) for p in range(start, end + 1)]
        blocks = merge_page_breaks(blocks_for_pages(pages))
        # drop a sub-heading that merely repeats the chapter title
        while blocks and blocks[0]['t'] == 'subhead' and \
                blocks[0]['text'].rstrip('!?.').lower() == title.rstrip('!?.').lower():
            blocks = blocks[1:]
        blocks, hits = prune.apply(slug, blocks)
        prune_hits.extend(hits)
        body = to_mdx(blocks)
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
            if start == 'custom':
                end = 'custom'
            else:
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

    unmatched = [h for h in prune_hits if h[3] == 0]
    if unmatched:
        for slug, kind, match, _ in unmatched:
            print(f'  ✗ prune rule never matched: [{slug}] {kind} {match[:70]!r}')
        raise SystemExit('prune rules out of date — fix tools/prune.py')
    print(f'pruned   : {len(prune_hits)} promo passages '
          f'({sum(h[3] for h in prune_hits)} blocks touched)')
    print(f'chapters : {len(manifest)}')
    print(f'words    : {sum(m["words"] for m in manifest):,}')
    print(f'figures  : {sum(m["figures"] for m in manifest)} in chapters, '
          f'{sum(1 for e in gl for b in e["blocks"] if b["t"] == "figure")} in glossary, '
          f'{len(used)} copied')
    print(f'glossary : {len(gl)} terms')


if __name__ == '__main__':
    main()
