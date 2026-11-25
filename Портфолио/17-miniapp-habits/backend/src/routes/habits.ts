import type { FastifyInstance } from 'fastify';
import {
  listHabits,
  createHabit,
  updateHabit,
  deleteHabit,
  toggleCheckin,
} from '../services/habits.js';
import { today } from '../services/streak.js';

/** Простейшая валидация «YYYY-MM-DD». */
function isValidDay(s: unknown): s is string {
  return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s);
}

export async function habitRoutes(app: FastifyInstance): Promise<void> {
  const db = app.db;

  // Список привычек текущего пользователя со статистикой.
  app.get('/habits', async (req) => {
    const habits = await listHabits(db, req.tgUser.id);
    return { habits };
  });

  // Создание привычки.
  app.post<{ Body: { title?: string; emoji?: string; color?: string } }>(
    '/habits',
    async (req, reply) => {
      const title = (req.body?.title ?? '').trim();
      if (!title) {
        return reply.code(400).send({ error: 'Название привычки обязательно' });
      }
      if (title.length > 80) {
        return reply.code(400).send({ error: 'Название слишком длинное (макс. 80)' });
      }
      const habit = await createHabit(db, req.tgUser.id, {
        title,
        emoji: req.body?.emoji,
        color: req.body?.color,
      });
      return reply.code(201).send({ habit });
    }
  );

  // Обновление привычки (в т.ч. архивация).
  app.patch<{
    Params: { id: string };
    Body: { title?: string; emoji?: string; color?: string; archived?: boolean };
  }>('/habits/:id', async (req, reply) => {
    const id = Number(req.params.id);
    if (!Number.isFinite(id)) {
      return reply.code(400).send({ error: 'Некорректный id' });
    }
    const title = req.body?.title?.trim();
    if (title !== undefined && title.length === 0) {
      return reply.code(400).send({ error: 'Название не может быть пустым' });
    }
    const habit = await updateHabit(db, req.tgUser.id, id, {
      title,
      emoji: req.body?.emoji,
      color: req.body?.color,
      archived: req.body?.archived,
    });
    if (!habit) return reply.code(404).send({ error: 'Привычка не найдена' });
    return { habit };
  });

  // Удаление привычки.
  app.delete<{ Params: { id: string } }>('/habits/:id', async (req, reply) => {
    const id = Number(req.params.id);
    if (!Number.isFinite(id)) {
      return reply.code(400).send({ error: 'Некорректный id' });
    }
    const ok = await deleteHabit(db, req.tgUser.id, id);
    if (!ok) return reply.code(404).send({ error: 'Привычка не найдена' });
    return { ok: true };
  });

  // Переключение отметки за день (по умолчанию — сегодня).
  app.post<{ Params: { id: string }; Body: { day?: string } }>(
    '/habits/:id/toggle',
    async (req, reply) => {
      const id = Number(req.params.id);
      if (!Number.isFinite(id)) {
        return reply.code(400).send({ error: 'Некорректный id' });
      }
      const day = req.body?.day ?? today();
      if (!isValidDay(day)) {
        return reply.code(400).send({ error: 'Некорректная дата (нужен YYYY-MM-DD)' });
      }
      const habit = await toggleCheckin(db, req.tgUser.id, id, day);
      if (!habit) return reply.code(404).send({ error: 'Привычка не найдена' });
      return { habit };
    }
  );
}
