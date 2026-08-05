/**
 * Language-aware access to the book: chapters, the plain-English layer, the
 * glossary and the diagram specs.
 *
 * The English edition is the structural source of truth — chapter order, page
 * ranges, figure counts and slugs all come from it, so a translation can never
 * renumber the book or break a link. A translation supplies text only, and
 * anything it hasn't translated falls back to the English original rather than
 * disappearing.
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import manifest from '../data/manifest.json';
import annotationsEn from '../data/annotations.json';
import annotationsPa from '../data/pa/annotations.json';
import glossaryEn from '../data/glossary.json';
import glossaryPa from '../data/pa/glossary.json';
import diagramsEn from '../data/diagrams.json';
import diagramsPa from '../data/pa/diagrams.json';
import type { Lang } from './i18n';

export type BookEntry = CollectionEntry<'book'> | CollectionEntry<'bookPa'>;

/** '018-testing-supply' -> 'testing-supply' */
export const slugOf = (id: string) => id.replace(/^\d+-/, '');

export interface Chapter {
  slug: string;
  /** the entry to render — the translation when there is one */
  entry: BookEntry;
  /** false when this chapter is still showing the English original */
  translated: boolean;
}

/** Every chapter in printed order, in the requested language. */
export async function chapters(lang: Lang): Promise<Chapter[]> {
  const en = (await getCollection('book')).sort((a, b) => a.data.order - b.data.order);
  if (lang === 'en') {
    return en.map((entry) => ({ slug: slugOf(entry.id), entry, translated: true }));
  }
  const translations = new Map(
    (await getCollection('bookPa')).map((e) => [slugOf(e.id), e]),
  );
  return en.map((entry) => {
    const t = translations.get(slugOf(entry.id));
    return { slug: slugOf(entry.id), entry: t ?? entry, translated: Boolean(t) };
  });
}

export type TocRow = (typeof manifest)[number];

/**
 * The table of contents: the shared manifest (order, pages, word counts) with
 * titles and section names taken from the translated frontmatter.
 */
export async function toc(lang: Lang): Promise<TocRow[]> {
  const titles = new Map((await chapters(lang)).map((c) => [c.slug, c.entry.data]));
  return manifest.map((ch) => ({
    ...ch,
    title: titles.get(ch.slug)?.title ?? ch.title,
    section: titles.get(ch.slug)?.section ?? ch.section,
  }));
}

/** The manifest grouped into the book's five sections, in order. */
export function bySection(rows: TocRow[]) {
  const out: { name: string; items: TocRow[] }[] = [];
  for (const ch of rows) {
    let s = out.find((x) => x.name === ch.section);
    if (!s) out.push((s = { name: ch.section, items: [] }));
    s.items.push(ch);
  }
  return out;
}

export interface Note { plain: string; remember: string[]; diagram?: string }

/** Plain-English summaries and takeaways. `diagram` always comes from English —
 *  it is a key into diagrams.json, not prose. */
export function annotations(lang: Lang): Record<string, Note> {
  const en = annotationsEn as Record<string, Note>;
  if (lang === 'en') return en;
  const pa = annotationsPa as Record<string, Partial<Note>>;
  const out: Record<string, Note> = {};
  for (const [slug, note] of Object.entries(en)) {
    const t = pa[slug];
    out[slug] = t
      ? { ...note, plain: t.plain ?? note.plain, remember: t.remember ?? note.remember }
      : note;
  }
  return out;
}

export interface GlossaryEntry {
  term: string;
  slug: string;
  page: number;
  blocks: { t: string; text?: string; src?: string; w?: number; h?: number; label?: string; caption?: string }[];
}

/** Glossary entries. Terms stay in English in every edition — they are the
 *  headwords a reader looks up — so only the blocks are replaced. */
export function glossary(lang: Lang): GlossaryEntry[] {
  const en = glossaryEn as GlossaryEntry[];
  if (lang === 'en') return en;
  const pa = new Map((glossaryPa as Partial<GlossaryEntry>[]).map((e) => [e.slug, e]));
  return en.map((e) => {
    const t = pa.get(e.slug);
    return t?.blocks ? { ...e, blocks: t.blocks as GlossaryEntry['blocks'] } : e;
  });
}

const isPlainObject = (v: unknown): v is Record<string, any> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

/**
 * Overlay a translation onto a diagram spec. Arrays merge by position, so a
 * translation file only carries the strings it changes — the geometry (bar
 * heights, volumes, tones) is never duplicated and so can never drift.
 */
function overlay(base: any, patch: any): any {
  if (patch === undefined || patch === null) return base;
  if (Array.isArray(base) && Array.isArray(patch)) {
    return base.map((item, i) => (i < patch.length ? overlay(item, patch[i]) : item));
  }
  if (isPlainObject(base) && isPlainObject(patch)) {
    const out = { ...base };
    for (const [k, v] of Object.entries(patch)) out[k] = k in base ? overlay(base[k], v) : v;
    return out;
  }
  return patch;
}

export function diagram(name: string, lang: Lang) {
  const spec = (diagramsEn as Record<string, any>)[name];
  if (lang === 'en' || !spec) return spec;
  return overlay(spec, (diagramsPa as Record<string, any>)[name]);
}
