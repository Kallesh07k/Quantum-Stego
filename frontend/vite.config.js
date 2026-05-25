// ============================================================
// FILE: frontend/vite.config.js
// PURPOSE: Configures Vite bundler for the React app
// ============================================================

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // @vitejs/plugin-react enables:
  // 1. JSX transformation (converts JSX syntax to React.createElement calls)
  // 2. Fast Refresh (hot reload — changes appear instantly without page refresh)

  server: {
    port: 5173,
    // The dev server runs on http://localhost:5173
    // Backend must be on http://localhost:8000 (different port = CORS needed)
  },
});
