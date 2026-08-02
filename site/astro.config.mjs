import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [mdx()],
  markdown: { smartypants: false },
  build: { inlineStylesheets: 'auto', format: 'directory' },
  // Cloudflare Pages serves /path/ from /path/index.html; being explicit keeps
  // the in-page links and the generated files agreeing with each other.
  trailingSlash: 'always',
});
