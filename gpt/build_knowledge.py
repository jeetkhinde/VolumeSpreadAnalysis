#!/usr/bin/env python3
"""Build the Custom GPT knowledge pack from the reader's own data.

Run:  python3 gpt/build_knowledge.py
Out:  gpt/knowledge/*.md

Everything here is generated, so re-running after a content change keeps the
GPT's knowledge in sync with the site.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')
OUT = os.path.join(HERE, 'knowledge')

BOOK = os.path.join(SITE, 'src', 'content', 'book')
DATA = os.path.join(SITE, 'src', 'data')

SECTION_FILES = {
    'Front Matter': '01-foundations.md',
    'Market Basics': '01-foundations.md',
    'Trends & Volume Spread Analysis': '02-trends.md',
    'The Anatomy of Bull & Bear Markets': '03-signals-in-context.md',
    'Becoming a Trader or Investor': '04-trading-practice.md',
    'Appendix': '04-trading-practice.md',
}


def strip_mdx(body: str) -> str:
    """Turn a chapter's MDX into plain prose, keeping figure captions."""
    body = re.sub(
        r'<Figure[^>]*?label="([^"]*)"[^>]*?caption="([^"]*)"[^>]*/>',
        r'\n[CHART — \1: \2]\n', body)
    body = re.sub(r'<Figure[^>]*/>', '\n[CHART]\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = json.load(open(f'{DATA}/manifest.json'))
    ann = json.load(open(f'{DATA}/annotations.json'))
    glossary = json.load(open(f'{DATA}/glossary.json'))

    files = {}
    for ch in manifest:
        fname = SECTION_FILES[ch['section']]
        path = os.path.join(BOOK, f"{ch['order']:03d}-{ch['slug']}.mdx")
        body = strip_mdx(open(path).read().split('---', 2)[2])
        note = ann.get(ch['slug'], {})
        pages = (f"p. {ch['printedStart']}" if ch['printedStart'] == ch['printedEnd']
                 else f"pp. {ch['printedStart']}–{ch['printedEnd']}")

        parts = [f"\n\n## {ch['order']}. {ch['title']}",
                 f"*Section: {ch['section']} · {pages} of the 4th edition*"]
        if note.get('plain'):
            parts.append(f"\n**In plain English:** {note['plain']}")
        if note.get('remember'):
            parts.append("\n**Things to remember:**\n" +
                         '\n'.join(f'- {r}' for r in note['remember']))
        parts.append("\n### Tom Williams' own words\n\n" + body)
        files.setdefault(fname, []).append('\n'.join(parts))

    headers = {
        '01-foundations.md': 'Master the Markets — Foundations (Preamble, Introduction, Market Basics)',
        '02-trends.md': 'Master the Markets — Trends & Volume Spread Analysis',
        '03-signals-in-context.md': 'Master the Markets — The Anatomy of Bull & Bear Markets',
        '04-trading-practice.md': 'Master the Markets — Becoming a Trader or Investor',
    }
    for fname, chunks in files.items():
        head = (f"# {headers[fname]}\n\n"
                "Tom Williams, *Master the Markets*, 4th edition (2009).\n"
                "Each chapter gives a plain-English summary and takeaways written for this\n"
                "edition, followed by Williams' own words verbatim. `[CHART — ...]` marks\n"
                "where a chart appears in the book.\n")
        open(os.path.join(OUT, fname), 'w').write(head + ''.join(chunks) + '\n')

    # glossary
    lines = ["# Master the Markets — Glossary of Terms\n",
             "All 61 entries from the back of the 4th edition, verbatim.\n"]
    for e in sorted(glossary, key=lambda x: x['term'].lower()):
        lines.append(f"\n## {e['term']}\n")
        for b in e['blocks']:
            if b['t'] == 'para':
                lines.append(b['text'] + '\n')
            elif b['t'] == 'bullet':
                lines.append(f"- {b['text']}\n")
            elif b['t'] == 'figure' and b.get('caption'):
                lines.append(f"[CHART — {b.get('label','')}: {b['caption']}]\n")
    open(os.path.join(OUT, '05-glossary.md'), 'w').write(''.join(lines))

    sizes = {f: os.path.getsize(os.path.join(OUT, f)) for f in sorted(os.listdir(OUT))}
    total_words = sum(len(open(os.path.join(OUT, f)).read().split())
                      for f in sizes if f.endswith('.md'))
    for f, s in sizes.items():
        print(f'  {f:28s} {s/1024:7.1f} KB')
    print(f'  {"TOTAL":28s} {sum(sizes.values())/1024:7.1f} KB, {total_words:,} words')


if __name__ == '__main__':
    main()
