import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const chapter = z.object({
  title: z.string(),
  section: z.string(),
  order: z.number(),
  printedStart: z.number(),
  printedEnd: z.number(),
  figures: z.number(),
});

const book = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/book' }),
  schema: chapter,
});

// The Punjabi edition: same filenames, same frontmatter shape, translated text.
// Order and page numbers are repeated here so the schema stays one thing, but
// the English collection is what the site actually numbers the book by.
const bookPa = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/book-pa' }),
  schema: chapter,
});

export const collections = { book, bookPa };
