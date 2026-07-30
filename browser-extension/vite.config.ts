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
        html = html.replace(/\s+crossorigin(?:="[^"]*")?/g, '');
        fs.writeFileSync(popupFlat, html, 'utf8');
        fs.rmSync(resolve(__dirname, 'dist/src/popup'), { recursive: true, force: true });
      }

      // 4. Flatten options HTML: dist/src/options/index.html → dist/options.html
      const optionsNested = resolve(__dirname, 'dist/src/options/index.html');
      const optionsFlat   = resolve(__dirname, 'dist/options.html');
      if (fs.existsSync(optionsNested)) {
        let html = fs.readFileSync(optionsNested, 'utf8');
        html = html.replace(/\.\.\/\.\.\/assets\//g, './assets/');
        html = html.replace(/\s+crossorigin(?:="[^"]*")?/g, '');
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
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    modulePreload: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      input: {
        popup:   resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
      },
      output: {
        entryFileNames: 'assets/js/[name]-[hash].js',
        chunkFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
});
