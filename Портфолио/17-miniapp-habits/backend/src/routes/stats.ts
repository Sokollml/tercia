import type { FastifyInstance } from 'fastify';
import { getStats } from '../services/habits.js';

export async function statsRoutes(app: FastifyInstance): Promise<void> {
  const db = app.db;

  // Текущий пользователь (профиль из Telegram).
  app.get('/me', async (req) => ({ user: req.tgUser }));

  // Сводная статистика + данные для недельного графика.
  app.get('/stats', async (req) => {
    const stats = await getStats(db, req.tgUser.id);
    return { stats };
  });
}
