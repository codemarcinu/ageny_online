import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3002,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
      },
      '/docs': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
      },
    },
  },
}) 