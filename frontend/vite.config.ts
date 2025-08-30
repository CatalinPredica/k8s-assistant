// Vite configuration for React project with backend API proxying during development
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Integrate React plugin for JSX and fast refresh support
  plugins: [react()],
  server: {
    // Proxy API requests to backend server to avoid CORS issues in development
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});