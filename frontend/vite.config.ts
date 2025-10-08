import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev in Docker behind Nginx
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    strictPort: true,
    allowedHosts: ['localhost', '127.0.0.1', 'vite_frontend'],
    hmr: { clientPort: 8080 },
  },
})
