import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Telegram открывает mini-app по HTTPS-URL (обычно Vercel/Netlify).
// base './' — чтобы ассеты работали при любом пути размещения.
export default defineConfig({
  base: './',
  plugins: [react()],
  server: { port: 5173 },
});
