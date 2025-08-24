import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // Ensure build output matches your backend's static folder
  },
  server: {
    port: 5173, // Local development port
    host: true,
  },
})
