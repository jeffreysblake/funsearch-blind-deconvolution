import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 7350,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:7351',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:7351',
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
