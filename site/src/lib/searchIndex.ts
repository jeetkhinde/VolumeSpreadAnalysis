/**
 * The search payload for one edition: chapters (text + plain-English layer)
 * followed by glossary entries. Each language gets its own index so a Punjabi
 * reader searching Gurmukhi isn't matched against English prose, while the
 * market vocabulary — kept in English in both editions — is findable either way.
 */
import { annotations, chapters, glossary } from './book';
import { href, t, type Lang } from './i18n';

const strip = (s: string) =>
  s
    .replace(/^---[\s\S]*?---/, '')            // frontmatter
    .replace(/<Figure[^>]*caption=\{?"([^"]*)"\}?[^>]*\/>/g, ' $1 ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/^[#>\-*]+\s*/gm, '')
    .replace(/\s+/g, ' ')
    .trim();

export async function searchIndex(lang: Lang) {
  const notes = annotations(lang);
  const docs = (await chapters(lang)).map(({ slug, entry }) => {
    const n = notes[slug];
    // The plain summary and takeaways are searchable too, so a reader can find
    // a chapter by the words they'd actually use.
    const extra = n ? ` ${n.plain} ${n.remember.join(' ')}` : '';
    return {
      title: entry.data.title,
      section: entry.data.section,
      url: href(lang, `/read/${slug}/`),
      text: strip(entry.body ?? '') + extra,
    };
  });

  for (const g of glossary(lang)) {
    docs.push({
      title: g.term,
      section: t(lang, 'sectionGlossary'),
      url: href(lang, `/glossary/#${g.slug}`),
      text: g.blocks.filter((b) => b.t !== 'figure').map((b) => b.text).join(' '),
    });
  }

  return docs;
}
