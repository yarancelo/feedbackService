import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In Docker the built static files are served by nginx and /api is routed by the
// reverse proxy. This dev-only proxy lets `npm run dev` talk to a local backend.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
})
