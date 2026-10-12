import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    // прокидываем запросы к Django API
    // в docker-compose хост называется `api`, локально (npm run dev) — localhost:8000
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://api:8000',
        changeOrigin: true,
      },
    },
  },
})
