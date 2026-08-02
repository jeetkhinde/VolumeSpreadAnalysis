# Master the Markets — online reader

Tom Williams' *Master the Markets* (4th edition, 2009, TradeGuider Systems) rebuilt
as a modern, responsive web reader — the full method text and every chart, with the
product marketing stripped out.

```bash
pip install -r tools/requirements.txt
python3 tools/run.py          # PDF -> MDX chapters + WebP figures + glossary
cd site && npm install && npm run dev
```

## What's here

```
Master the Markets by Tom Williams.pdf   source (12 MB, 185 pages)
tools/                                   PDF extraction pipeline
  paths.py      shared paths
  lines.py      per-line text + geometry + font size  -> .cache/lines.json
  charts.py     renders chart figures                 -> .cache/figs/
  build.py      assembles MDX + glossary + WebP       -> site/
  run.py        runs all three
site/                                    Astro 5 site
  src/content/book/*.mdx                 68 chapters
  src/data/glossary.json                 61 glossary entries
  public/figures/*.webp                  82 charts
```

## What was kept, and what wasn't

| | Printed pages | |
|---|---|---|
| Preamble, Introduction | 8–10 | kept |
| Section 1 — Market Basics | 12–48 | kept |
| Section 2 — Trends & Volume Spread Analysis | 50–68 | kept |
| Section 3 — The Anatomy of Bull & Bear Markets | 70–98 | kept |
| Section 4 — Becoming a Trader or Investor | 100–120 | kept |
| Section 5 — The TradeGuider System | 121–137 | **dropped** — product brochure |
| Suggested Reading List | 138 | kept (Wyckoff, Neill, et al.) |
| Do Not Ignore These Trading Facts! | 140 | kept |
| Glossary of Terms | 142–180 | kept, with its illustrations |
| Index | 181–185 | **dropped** — page-number pointers, meaningless online |

Section 5 is the only marketing removed: *Features List*, *Product Detail*,
*Data Provision*, *Broker Alliances*, *Customer Testimonials*. Inline mentions of
TradeGuider inside the method chapters are left intact — they're woven into
Williams' own sentences, and cutting them would damage the text.

### Completeness

Reconciled against the source PDF rather than assumed:

- **38,964 words** across 68 chapters vs 38,701 extractable words in the kept page
  ranges (the small surplus is markdown list markers).
- **82 of 82** non-brochure figures carried over — 47 in chapters, 35 in the glossary.
- **61 of 61** glossary entries, 5,927 words vs 5,930 in the source.

## Extraction notes

Two decisions did most of the work:

**Charts are rendered, not extracted.** The embedded rasters are only the bare
screenshots — Williams' annotation arrows, callout boxes and labels ("High",
"Low", "Price Bars") are vector objects drawn *on top* in the PDF. Pulling the
raster alone silently loses them. `charts.py` instead renders the page region at
216 DPI, growing the crop to include overlapping vector paths and clamping it
against neighbouring text so captions don't bleed in.

**Paragraphs are reconstructed from geometry.** `pypdf`'s text layer inserts
spurious spaces mid-word ("A price c hart is sim ply a vi sual..."); pdfium's is
clean but drops blank lines. `lines.py` takes pdfium's text and rebuilds structure
from character boxes — line pitch is ~11.5pt, so a gap over 16pt starts a new
paragraph; body glyphs run ~4.7pt, chapter titles 22–31pt, glossary terms 9–15pt.
Figures are placed by their position on the page, not by matching captions, so
uncaptioned illustrations survive.

## Reader features

Zero client JS for the content itself; the interactive bits are ~4 KB of vanilla script.

- Full-text search across chapters and glossary (`/`), keyboard-navigable
- Chapter nav with `←` / `→`, glossary with `g`
- Light/dark theme, respects system preference, remembered
- Click any chart to enlarge
- Reading progress bar, resumes where you left off
- Every chapter cites its printed page range, so you can check any passage against the PDF

## Deploying to Cloudflare Pages

The generated chapters and figures are committed, so the build needs Node only —
no Python step in CI.

**Git integration (recommended).** In the Cloudflare dashboard → Workers & Pages →
Create → Pages → connect this repo, then:

| Setting | Value |
|---|---|
| Framework preset | Astro |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Root directory | `site` |

`site/.nvmrc` pins Node 22. Nothing else needs configuring.

**From the CLI instead:**

```bash
cd site && npm run deploy      # astro build && wrangler pages deploy dist
```

### Keeping it private

`public/_headers` sends `X-Robots-Tag: noindex, nofollow`, every page carries a
`noindex` meta tag, and `public/robots.txt` disallows all crawlers. That stops it
being indexed — it does **not** stop anyone who has the URL.

For actual access control, put [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/policies/access/)
in front of the project (Zero Trust → Access → Applications → Self-hosted, pointed
at the `pages.dev` hostname). A one-time-PIN policy against your own email address
takes about a minute and keeps the deployment genuinely private, which given the
licence position below is the sensible default.

### Caching

`_headers` pins `/_astro/*` for a year (those filenames are content-hashed) and
`/figures/*` for a week — figure filenames come from page numbers rather than
content hashes, so a re-render reuses the name and must not be cached immutably.

## Licence

The text and charts are © 1993–2009 Tom Williams / TradeGuider Systems Ltd, and
the book carries an all-rights-reserved notice. TradeGuider distributes the PDF
free from their own site, but that is not the same as a licence to republish.
This repo is a personal reading copy — **settle redistribution with TradeGuider
before putting it on a public URL.** The code in `tools/` is yours to do
whatever you like with.
