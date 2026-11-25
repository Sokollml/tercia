import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Конфиг Vite. base='./' — относительные пути, чтобы сборка работала на любом
// хостинге (Vercel, GitHub Pages, поддиректория) без правок.
export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    port: 5173,
    host: true,
  },
});
