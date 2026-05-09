import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: { port: 5173, host: '127.0.0.1' },
  esbuild: { loader: 'jsx', include: /src\/.*\.[jt]sx?$/, exclude: [] },
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
})
