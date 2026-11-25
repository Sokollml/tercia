import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import type { Db } from '../db.js';
import { config } from '../config.js';
import { validateInitData, type TelegramUser } from './initData.js';
import { upsertUser } from '../services/habits.js';

/**
 * Авторизация по Telegram initData.
 *
 * Каждый запрос к /api/* ДОЛЖЕН содержать заголовок `X-Telegram-Init-Data`
 * со строкой window.Telegram.WebApp.initData. Мы проверяем её подпись (HMAC),
 * и только при валидной подписи пропускаем запрос дальше, положив пользователя
 * в req.tgUser. Так все ручки защищены единообразно, и подделать личность
 * нельзя, не зная BOT_TOKEN.
 */

// Расширяем типы Fastify: добавляем db на инстанс и tgUser на запрос.
declare module 'fastify' {
  interface FastifyInstance {
    db: Db;
  }
  interface FastifyRequest {
    tgUser: TelegramUser;
  }
}

export function registerAuth(app: FastifyInstance, db: Db): void {
  app.decorate('db', db);
  // Значение по умолчанию, чтобы TS был доволен до установки в хуке.
  app.decorateRequest('tgUser', null as unknown as TelegramUser);

  app.addHook('onRequest', async (req: FastifyRequest, reply: FastifyReply) => {
    // Пропускаем preflight и всё, что не /api (напр. /health).
    if (req.method === 'OPTIONS') return;
    if (!req.url.startsWith('/api')) return;

    const header = req.headers['x-telegram-init-data'];
    const initData = Array.isArray(header) ? header[0] : header;

    if (!initData) {
      reply.code(401).send({ error: 'Требуется заголовок X-Telegram-Init-Data' });
      return reply;
    }

    const result = validateInitData(
      initData,
      config.botToken,
      config.initDataMaxAgeSec
    );
    if (!result.ok) {
      reply.code(401).send({ error: result.error });
      return reply;
    }

    // Профиль пользователя актуализируем в БД и кладём в запрос.
    req.tgUser = result.data.user;
    await upsertUser(db, result.data.user);
  });
}
