/**
 * vite.content.config.ts
 *
 * Separate Vite build ONLY for the Chrome content script.
 *
 * WHY A SEPARATE BUILD?
 * Chrome content scripts are injected as plain <script> tags by the browser engine.
 * They DO NOT support ES module syntax (`import`/`export`) unless the manifest entry
 * explicitly sets "type": "module" (Chrome 112+ only and with caveats).
 *
 * The main vite.config.ts builds popup/options/background as ES modules (correct).
 * This config builds content/index.ts as a self-contained IIFE — all dependencies are
 * inlined, no import statements appear in the output.
 *
 * Build order in package.json:
 *   1. vite build               → popup, options, background (ES modules, clears dist/)
 *   2. vite build --config vite.content.config.ts → content.js IIFE (appends to dist/)
 */

import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    // IMPORTANT: do NOT clear dist — the main build already put popup/options/background there
    emptyOutDir: false,

    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
        passes: 2,
        unsafe_arrows: true,
      },
      mangle: { safari10: true },
      format: { comments: false },
    },

    // lib mode = single self-contained IIFE output (no import/export in output)
    lib: {
      entry: resolve(__dirname, 'src/content/index.ts'),
      name: 'CounterGuardContent',   // IIFE global name (unused by Chrome, required by Rollup)
      formats: ['iife'],
      fileName: () => 'content.js',  // Output: dist/content.js
    },

    rollupOptions: {
      // Inline ALL imports — content.js must be fully self-contained
      output: {
        inlineDynamicImports: true,
        entryFileNames: 'content.js',
      },
    },
  },
});
