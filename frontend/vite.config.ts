import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

const ENDERECO_DA_API_LOCAL = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: { '/api': ENDERECO_DA_API_LOCAL },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/testes/configurar.ts'],
    restoreMocks: true,
  },
})
