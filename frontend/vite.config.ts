/**
 * Vite configuration.
 *
 * Zgodność z wymaganiami:
 * - Development server configuration
 * - Build optimization
 * - Environment variables handling
 */

import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Path aliases
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@context": path.resolve(__dirname, "./src/context"),
      "@api": path.resolve(__dirname, "./src/api"),
      "@types": path.resolve(__dirname, "./src/types"),
      "@utils": path.resolve(__dirname, "./src/utils"),
    },
  },

  // Development server
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    strictPort: false, // Try next port if 3000 is busy
    proxy: {
      // Proxy API requests to backend (development)
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },

  // Preview server (after build)
  preview: {
    port: 4173,
    host: true,
    strictPort: false,
  },

  // Build options
  build: {
    outDir: "dist",
    sourcemap: true, // Generate sourcemaps for debugging
    minify: "esbuild", // Fast minification
    target: "esnext",

    // Chunk size warnings
    chunkSizeWarningLimit: 1000,

    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunking for better caching
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "date-vendor": ["date-fns"],
          "icons-vendor": ["lucide-react"],
        },
      },
    },
  },

  // Optimizations
  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom", "date-fns", "lucide-react"],
  },

  // Environment variables prefix
  envPrefix: "VITE_",

  // CSS options
  css: {
    devSourcemap: true,
  },
});
