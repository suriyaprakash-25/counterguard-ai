import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import fs from 'fs';

// Custom plugin to copy manifest.json and static files to build output root
function copyExtensionAssets() {
  return {
    name: 'copy-extension-assets',
    closeBundle() {
      const manifestSrc = resolve(__dirname, 'public/manifest.json');
      const manifestDest = resolve(__dirname, 'dist/manifest.json');
      if (fs.existsSync(manifestSrc)) {
        fs.copyFileSync(manifestSrc, manifestDest);
      }

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
    }
  };
}

export default defineConfig({
  plugins: [react(), copyExtensionAssets()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Terser minification for maximum compression
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,       // Remove console.* in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
        passes: 2,
        unsafe_arrows: true,
        unsafe_methods: true,
      },
      mangle: {
        safari10: true,
      },
      format: {
        comments: false,          // Strip all comments
      },
    },
    chunkSizeWarningLimit: 200,
    rollupOptions: {
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
      },
      input: {
        popup: resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
        background: resolve(__dirname, 'src/background/index.ts'),
        content: resolve(__dirname, 'src/content/index.ts'),
      },
      output: {
        // Chunk splitting for source files (not node_modules — those are pre-bundled by Vite)
        manualChunks(id) {
          // Extension services — shared by popup + content
          if (id.includes('/src/services/')) {
            return 'extension-services';
          }
          // Extension API layer
          if (id.includes('/src/api/')) {
            return 'extension-api';
          }
          // Parsers — heaviest non-vendor chunk, lazy loaded
          if (id.includes('/src/parsers/')) {
            return 'extension-parsers';
          }
          // Popup tab components — split per lazy tab
          if (id.includes('/src/popup/tabs/InspectTab')) {
            return 'popup-tab-inspect';
          }
          if (id.includes('/src/popup/tabs/HistoryTab')) {
            return 'popup-tab-history';
          }
        },
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'background.js';
          if (chunkInfo.name === 'content') return 'content.js';
          return 'assets/js/[name]-[hash].js';
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
});
