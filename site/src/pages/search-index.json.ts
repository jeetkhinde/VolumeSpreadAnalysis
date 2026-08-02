import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import glossary from '../data/glossary.json';

const strip = (s: string) =>
  s
    .replace(/^---[\s\S]*?---/, '')            // frontmatter
    .replace(/<Figure[^>]*caption=\{?"([^"]*)"\}?[^>]*\/>/g, ' $1 ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/^[#>\-*]+\s*/gm, '')
    .replace(/\s+/g, ' ')
    .trim();

export const GET: APIRoute = async () => {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const book = (await getCollection('book')).sort((a, b) => a.data.order - b.data.order);

  const docs = book.map((e) => ({
    title: e.data.title,
    section: e.data.section,
    url: `${base}/read/${e.id.replace(/^\d+-/, '')}/`,
    text: strip(e.body ?? ''),
  }));

  for (const g of glossary as any[]) {
    docs.push({
      title: g.term,
      section: 'Glossary',
      url: `${base}/glossary/#${g.slug}`,
      text: g.blocks.filter((b: any) => b.t !== 'figure').map((b: any) => b.text).join(' '),
    });
  }

  return new Response(JSON.stringify(docs), {
    headers: { 'Content-Type': 'application/json' },
  });
};
