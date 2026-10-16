/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://backend:8000" },
    // The dev server runs in Docker: file events from the host's bind mount do not reach it.
    watch: { usePolling: true, interval: 300 },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["src/test-setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
    restoreMocks: true,
    coverage: {
      include: ["src/**"],
      exclude: ["src/api/schema.d.ts", "src/test/**", "src/**/*.test.{ts,tsx}"],
      reporter: ["text-summary"],
    },
  },
});
