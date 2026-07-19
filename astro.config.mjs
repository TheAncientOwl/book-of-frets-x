// @ts-check
import { defineConfig } from 'astro/config';
import icon from 'astro-icon';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // <GitHub-Pages>
  site: 'https://TheAncientOwl.github.io',
  base: '/book-of-frets-x/',
  // </GitHub-Pages>

  integrations: [icon()],
  build: {
    inlineStylesheets: 'always',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
