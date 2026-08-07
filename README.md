# Master the Markets — online reader

Tom Williams' *Master the Markets* (4th edition, 2009, TradeGuider Systems) rebuilt
as a modern, responsive web reader — the full method text and every chart, with the
product marketing stripped out, plus a plain-English layer written for this edition.
Readable in English or Punjabi.

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
  src/content/book-pa/*.mdx              the same 68, in Punjabi
  src/data/glossary.json                 61 glossary entries
  src/data/annotations.json              plain-English summaries + takeaways
  src/data/diagrams.json                 66 diagram specs (data, not drawings)
  src/data/pa/*.json                     Punjabi overrides for the three above
  src/data/i18n/ui.json                  interface strings, en + pa
  src/data/i18n/keep-terms.json          market vocabulary that stays in English
  src/lib/i18n.ts                        language registry, URL + string helpers
  src/lib/book.ts                        language-aware content access
  src/components/BarDiagram.astro        renders panels + sequence as SVG
  src/components/ConceptDiagram.astro    renders flow + compare as HTML
  src/components/Diagram.astro           dispatch + the two hand-drawn ones
  public/figures/*.webp                  82 charts
tools/check-translation.mjs              build-time parity guard
```

## The plain-English layer

Every chapter opens with an **In plain English** summary and closes with
**Things to remember** — 2,844 words of summary and 215 takeaways across the 68
chapters, in short conversational sentences.

This is added *alongside* Williams' text, never in place of it. Rewriting his
prose would risk quietly changing the exact bar conditions the method depends on
(spread, close position, volume, and the required background), and would throw
away the completeness guarantee below. You get the plain version first and his
precise wording underneath.

**All 68 chapters carry a diagram** drawn for this edition. They are theme-aware,
labelled as not being from the book, and every takeaway is also collected on one
**Key Points** page that doubles as a visual cheat-sheet.

They are described as *data*, not drawn by hand. `src/data/diagrams.json` holds a
spec per diagram and two renderers lay them out, so adding one costs a few lines
of JSON. Four shapes cover the whole book:

| Shape | For | Example |
|---|---|---|
| `panels` | bar signatures side by side | a genuine test vs a failed test |
| `sequence` | a run of bars with zones, trend lines, callouts | shake-out, absorption, up-thrust |
| `flow` | a process with steps and arrows | how a campaign is run, the long checklist |
| `compare` | two sides of an argument | what the news says vs what the volume says |

`BarDiagram.astro` renders `panels` and `sequence` as SVG, auto-fitting the price
axis to the data and sharing one scale across panels so they stay comparable.
`ConceptDiagram.astro` renders `flow` and `compare` as HTML rather than SVG,
because they are text-heavy and need to wrap and reflow on mobile. Flows of four
or more steps stack vertically — wrapping a horizontal flow leaves an arrow
pointing at nothing.

Only *how to read one price bar* and *the market cycle* are hand-drawn.

## The Punjabi edition

The whole book is also readable in Punjabi. English stays at its existing URLs;
Punjabi lives under `/pa/`, and the 🌐 switcher in the header is a real link to
the same page in the other language, so either version can be bookmarked or
shared. The choice is remembered, but nothing is ever auto-redirected — landing
on an English URL gives you English.

**Market vocabulary is not translated.** *Market, price, trend, uptrend,
downtrend, up-thrust, volume, spread, bar, high, low, timeframe, professional,
market-maker, supply, demand, accumulation, distribution, test, shake-out* and
the rest of the method's terms stay in Latin script. They are what you will see
on a chart, in a broker's platform and in every other book on the subject;
inventing Punjabi equivalents would make the text unsearchable and teach names
nobody else uses. `src/data/i18n/keep-terms.json` is the list. Punjabi grammar
carries the sentence and inflects *around* those terms, never inside them —
"volume ਉੱਚਾ ਹੈ", not a transliterated stem with a case ending glued on.

Translated: 68 chapters, the plain-English layer for all 68 (now plain
Punjabi), 61 glossary entries, 66 diagrams and the interface itself.

English is the structural source of truth. Chapters, annotations, glossary
entries and diagrams are all looked up by their English key, and anything
without a translation falls back to English *visibly*, with a notice, rather
than vanishing. Diagram translations are an index-wise overlay onto the English
spec — only the labels are duplicated, never the geometry, so a diagram cannot
drift between the two languages.

`tools/check-translation.mjs` runs before the build and fails it on: a missing
or extra chapter; a changed `order`, printed page range or figure count; figures
in a different order or pointing at different files; one English section mapped
to two Punjabi names; a missing annotation, glossary or diagram key; a glossary
entry whose block structure or figure sources drifted; and a spot check that the
keep-terms really did survive translation.

Search is per-language and normalises Unicode properly (`\p{L}\p{N}\p{M}`), so
Gurmukhi matras don't break matching. `html[lang="pa"]` relaxes line height and
letter spacing, and the font stack puts Latin faces first so the untranslated
market terms keep their shape.

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

Section 5 is dropped wholesale: *Features List*, *Product Detail*, *Data
Provision*, *Broker Alliances*, *Customer Testimonials*.

The product plugs woven into the method chapters are removed too — 24 rules in
`tools/prune.py`, 696 words in total. Each rule is explicit and verified at build
time, so if one stops matching the build fails rather than silently keeping or
losing text. Where a sentence mixes advertising with method ("...turn on the
instant trend indicator. On any reaction, if the low is higher than the last
reaction, this is an uptrend"), only the advertising half is cut.

### Completeness

Reconciled against the source PDF rather than assumed:

- **38,268 words** across 68 chapters, after removing 696 words of product
  marketing (38,964 before the prune, against 38,701 extractable words in the kept
  page ranges — the small surplus is markdown list markers).
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

- Body text set at 20px with 1.8 line height on a ~65-character measure
- English and Punjabi, switchable from any page (🌐), remembered
- Full-text search across chapters and glossary (`/`), keyboard-navigable
- Chapter nav with `←` / `→`, glossary with `g`
- Light/dark theme, respects system preference, remembered
- Click any chart to enlarge
- Reading progress bar, resumes where you left off
- Every chapter cites its printed page range, so you can check any passage against the PDF

## Deploying to Cloudflare

Deployed as a **static-assets-only Worker** (service `vsa`) — no server code, just
`site/dist` served from the edge. The generated chapters and figures are committed,
so CI needs Node only; there is no Python step.

`wrangler.jsonc` declares the assets directory. It is duplicated in two places
because the Workers Builds **Root directory** setting decides which one is read:

| Root directory | Config used | Assets path |
|---|---|---|
| `/` (default) | `wrangler.jsonc` | `./site/dist` |
| `site` | `site/wrangler.jsonc` | `./dist` |

Both are committed so either setting works. If you change one, change the other —
`name` and `compatibility_date` must stay in sync.

Build settings, either root:

| Setting | Value |
|---|---|
| Build command | `npm run build` |
| Deploy command | `npx wrangler deploy` |

The repo-root `package.json` delegates into `site/` (`npm ci && npm run build`), so
`npm run build` works from either directory. `.nvmrc` pins Node 22 at both levels.

**From the CLI:**

```bash
npm run deploy            # from the repo root
cd site && npm run deploy # or from site/, using Pages instead
```

`html_handling: auto-trailing-slash` matches Astro's directory-style URLs, and
`not_found_handling: 404-page` serves the generated `404.html`.

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
