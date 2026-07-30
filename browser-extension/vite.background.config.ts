/**
 * vite.background.config.ts — Dedicated Single-Bundle Build for Chrome Service Worker
 * Forces inlineDynamicImports to ensure background.js has ZERO external asset chunk imports,
 * preventing Chrome "An unknown error occurred when fetching the script" errors.
 */

import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      input: {
        background: resolve(__dirname, 'src/background/index.ts'),
      },
      output: {
        entryFileNames: 'background.js',
        format: 'es',
        inlineDynamicImports: true,
      },
    },
  },
});
