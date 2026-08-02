import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const book = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/book' }),
  schema: z.object({
    title: z.string(),
    section: z.string(),
    order: z.number(),
    printedStart: z.number(),
    printedEnd: z.number(),
    figures: z.number(),
  }),
});

export const collections = { book };
