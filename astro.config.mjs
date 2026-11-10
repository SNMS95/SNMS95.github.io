// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { unified } from '@astrojs/markdown-remark';

// User site: served from the root of https://snms95.github.io (repo name SNMS95.github.io).
export default defineConfig({
  site: 'https://snms95.github.io',
  integrations: [sitemap()],
  markdown: {
    // Astro 7's default Markdown processor has no remark/rehype support; math needs the unified one.
    processor: unified({ remarkPlugins: [remarkMath], rehypePlugins: [rehypeKatex] }),
    shikiConfig: {
      // Dual themes; global.css switches them with the colour scheme.
      themes: { light: 'github-light', dark: 'github-dark' },
      defaultColor: false,
    },
  },
});
