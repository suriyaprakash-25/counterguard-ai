import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import fs from 'fs';

/**
 * Copy manifest.json and icons/ into dist/ root.
 * Also flattens popup/options HTML from dist/src/{popup,options}/index.html
 * → dist/popup.html and dist/options.html so manifest paths are simple.
 */
function copyExtensionAssets() {
  return {
    name: 'copy-extension-assets',
    closeBundle() {
      // 1. manifest.json → dist/
      const manifestSrc = resolve(__dirname, 'public/manifest.json');
      const manifestDest = resolve(__dirname, 'dist/manifest.json');
      if (fs.existsSync(manifestSrc)) {
        fs.copyFileSync(manifestSrc, manifestDest);
      }

      // 2. icons/ → dist/icons/
      const iconsSrc = resolve(__dirname, 'public/icons');
      const iconsDest = resolve(__dirname, 'dist/icons');
      if (fs.existsSync(iconsSrc)) {
        if (!fs.existsSync(iconsDest)) {
          fs.mkdirSync(iconsDest, { recursive: true });
        }
        fs.readdirSync(iconsSrc).forEach(file => {
          fs.copyFileSync(resolve(iconsSrc, file), resolve(iconsDest, file));
        });
      }

      // 3. Flatten popup HTML: dist/src/popup/index.html → dist/popup.html
      //    Also fix paths: base './' generates ../../assets/ relative to src/popup/ nesting
      //    After move to dist root, ../../assets/ is wrong → rewrite to ./assets/
      const popupNested = resolve(__dirname, 'dist/src/popup/index.html');
      const popupFlat   = resolve(__dirname, 'dist/popup.html');
      if (fs.existsSync(popupNested)) {
        let html = fs.readFileSync(popupNested, 'utf8');
        html = html.replace(/\.\.\/\.\.\/assets\//g, './assets/');
        fs.writeFileSync(popupFlat, html, 'utf8');
        fs.rmSync(resolve(__dirname, 'dist/src/popup'), { recursive: true, force: true });
      }

      // 4. Flatten options HTML: dist/src/options/index.html → dist/options.html
      const optionsNested = resolve(__dirname, 'dist/src/options/index.html');
      const optionsFlat   = resolve(__dirname, 'dist/options.html');
      if (fs.existsSync(optionsNested)) {
        let html = fs.readFileSync(optionsNested, 'utf8');
        html = html.replace(/\.\.\/\.\.\/assets\//g, './assets/');
        fs.writeFileSync(optionsFlat, html, 'utf8');
        fs.rmSync(resolve(__dirname, 'dist/src/options'), { recursive: true, force: true });
      }

      // 5. Clean up empty dist/src/ dir if empty
      const distSrc = resolve(__dirname, 'dist/src');
      if (fs.existsSync(distSrc)) {
        try { fs.rmdirSync(distSrc); } catch { /* non-empty, leave it */ }
      }
    }
  };
}

export default defineConfig({
  plugins: [react(), copyExtensionAssets()],
  // CRITICAL: base must be './' so Vite outputs relative paths (./assets/...)
  // Absolute paths (/assets/...) break under chrome-extension:// protocol
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Use relative base so all asset paths are relative (critical for chrome-extension:// protocol)
    // Note: We set base at the rollup output level via relative paths in HTML
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
        passes: 2,
        unsafe_arrows: true,
        unsafe_methods: true,
      },
      mangle: { safari10: true },
      format: { comments: false },
    },
    chunkSizeWarningLimit: 200,
    rollupOptions: {
      input: {
        popup:   resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
        background: resolve(__dirname, 'src/background/index.ts'),
        // content script is built separately in vite.content.config.ts as IIFE
      },
      output: {
        // Ensure entry files go to correct locations
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'background.js';
          return 'assets/js/[name]-[hash].js';
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        // DO NOT use manualChunks that generates empty chunks — simplify to just vendor split
        manualChunks(id) {
          // Vendor: react, react-dom, lucide-react etc → one shared vendor chunk
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          // Extension services shared between popup + background
          if (id.includes('/src/services/')) return 'ext-services';
          if (id.includes('/src/api/'))      return 'ext-api';
        },
      },
    },
  },
});
