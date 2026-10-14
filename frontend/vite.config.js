import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";
export default defineConfig({
  base: "/static/ui/",
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  build: { outDir: "../app/static/ui", emptyOutDir: true, sourcemap: false },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/static/personal-store.js": "http://127.0.0.1:8000",
      "/static/app.js": "http://127.0.0.1:8000",
      "/static/library.js": "http://127.0.0.1:8000",
      "/static/study.js": "http://127.0.0.1:8000",
      "/static/favicon.svg": "http://127.0.0.1:8000",
    },
  },
});
