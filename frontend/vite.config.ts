import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

const ENDERECO_DA_API_LOCAL = 'http://localhost:8000'
const REPASSE_DA_API = { '/api': ENDERECO_DA_API_LOCAL }

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: REPASSE_DA_API,
  },
  preview: {
    port: 4173,
    strictPort: true,
    proxy: REPASSE_DA_API,
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/testes/configurar.ts'],
    restoreMocks: true,
  },
})
