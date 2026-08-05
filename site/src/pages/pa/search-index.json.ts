import type { APIRoute } from 'astro';
import { searchIndex } from '../../lib/searchIndex';

export const GET: APIRoute = async () =>
  new Response(JSON.stringify(await searchIndex('pa')), {
    headers: { 'Content-Type': 'application/json' },
  });
