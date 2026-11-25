import Fastify, { type FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import { config } from './config.js';
import type { Db } from './db.js';
import { registerAuth } from './auth/authPlugin.js';
import { habitRoutes } from './routes/habits.js';
import { statsRoutes } from './routes/stats.js';

/**
 * Фабрика Fastify-приложения. Отделена от запуска сервера, чтобы приложение
 * можно было собирать в тестах и дёргать через app.inject(...) без сети.
 */
export function buildApp(db: Db): FastifyInstance {
  const app = Fastify({
    logger: process.env.NODE_ENV === 'test' ? false : { level: 'info' },
  });

  // CORS: разрешаем домены mini-app из MINIAPP_URL и наш кастомный заголовок.
  app.register(cors, {
    origin: config.miniappUrls.length > 0 ? config.miniappUrls : true,
    methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'X-Telegram-Init-Data'],
  });

  // Публичный health-check (без авторизации).
  app.get('/health', async () => ({ ok: true, ts: Date.now() }));

  // Авторизация по initData для всех /api/*.
  registerAuth(app, db);

  // Защищённые ручки.
  app.register(habitRoutes, { prefix: '/api' });
  app.register(statsRoutes, { prefix: '/api' });

  return app;
}
