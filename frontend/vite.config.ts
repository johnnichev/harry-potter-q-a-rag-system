import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  test: {
    environment: 'jsdom',
    css: true,
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 90, branches: 90, functions: 90, statements: 90,
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/main.tsx', 'src/components/Answer.tsx', 'src/api/client.ts', 'src/types.ts']
    },
    setupFiles: ['./src/test/setup.ts']
  }
})
