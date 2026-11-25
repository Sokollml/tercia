import { describe, it, expect, beforeAll } from 'vitest';

/**
 * Интеграционный тест полного стека на SQLite in-memory.
 * Проверяем, что все /api/* ручки защищены initData и что бизнес-логика
 * (создание, отметка, статистика) работает через реальный Fastify + БД.
 *
 * ВАЖНО: переменные окружения выставляем ДО импорта модулей, которые читают
 * config при инициализации.
 */

const BOT_TOKEN = '123456:TEST_TOKEN_abcdefghijklmnopqrstuvwxyz';

process.env.NODE_ENV = 'test';
process.env.BOT_TOKEN = BOT_TOKEN;
process.env.DB_DRIVER = 'sqlite';
process.env.SQLITE_PATH = ':memory:';
process.env.INITDATA_MAX_AGE_SEC = '0';
process.env.MINIAPP_URL = 'http://localhost:5173';

let app: import('fastify').FastifyInstance;
let auth: string;

function signValidInitData(sign: (f: Record<string, string>, t: string) => string) {
  return sign(
    {
      user: JSON.stringify({ id: 7, first_name: 'Ада', username: 'ada' }),
      auth_date: Math.floor(Date.now() / 1000).toString(),
    },
    BOT_TOKEN
  );
}

beforeAll(async () => {
  const { getDb } = await import('../src/db.js');
  const { migrate } = await import('../src/migrate.js');
  const { buildApp } = await import('../src/app.js');
  const { signInitData } = await import('../src/auth/initData.js');

  const db = await getDb();
  await migrate();
  app = buildApp(db);
  await app.ready();

  auth = signValidInitData(signInitData);
});

describe('авторизация', () => {
  it('отклоняет запрос без initData (401)', async () => {
    const res = await app.inject({ method: 'GET', url: '/api/habits' });
    expect(res.statusCode).toBe(401);
  });

  it('отклоняет запрос с подделанным initData (401)', async () => {
    const res = await app.inject({
      method: 'GET',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth + 'ff' },
    });
    expect(res.statusCode).toBe(401);
  });

  it('health доступен без авторизации', async () => {
    const res = await app.inject({ method: 'GET', url: '/health' });
    expect(res.statusCode).toBe(200);
  });
});

describe('CRUD привычек и отметки', () => {
  it('пустой список для нового пользователя', async () => {
    const res = await app.inject({
      method: 'GET',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth },
    });
    expect(res.statusCode).toBe(200);
    expect(res.json().habits).toEqual([]);
  });

  it('создаёт привычку, отмечает сегодня, стрик = 1', async () => {
    const created = await app.inject({
      method: 'POST',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth, 'content-type': 'application/json' },
      payload: { title: 'Пить воду', emoji: '💧', color: '#00B894' },
    });
    expect(created.statusCode).toBe(201);
    const habit = created.json().habit;
    expect(habit.title).toBe('Пить воду');
    expect(habit.todayDone).toBe(false);
    expect(habit.currentStreak).toBe(0);

    const toggled = await app.inject({
      method: 'POST',
      url: `/api/habits/${habit.id}/toggle`,
      headers: { 'x-telegram-init-data': auth, 'content-type': 'application/json' },
      payload: {},
    });
    expect(toggled.statusCode).toBe(200);
    expect(toggled.json().habit.todayDone).toBe(true);
    expect(toggled.json().habit.currentStreak).toBe(1);
  });

  it('повторный toggle снимает отметку', async () => {
    const list = await app.inject({
      method: 'GET',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth },
    });
    const id = list.json().habits[0].id;

    const off = await app.inject({
      method: 'POST',
      url: `/api/habits/${id}/toggle`,
      headers: { 'x-telegram-init-data': auth, 'content-type': 'application/json' },
      payload: {},
    });
    expect(off.json().habit.todayDone).toBe(false);
    expect(off.json().habit.currentStreak).toBe(0);
  });

  it('отклоняет создание без названия (400)', async () => {
    const res = await app.inject({
      method: 'POST',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth, 'content-type': 'application/json' },
      payload: { title: '   ' },
    });
    expect(res.statusCode).toBe(400);
  });

  it('отдаёт статистику с недельным графиком на 7 дней', async () => {
    const res = await app.inject({
      method: 'GET',
      url: '/api/stats',
      headers: { 'x-telegram-init-data': auth },
    });
    expect(res.statusCode).toBe(200);
    const stats = res.json().stats;
    expect(stats.week).toHaveLength(7);
    expect(typeof stats.totalHabits).toBe('number');
  });

  it('удаляет привычку', async () => {
    const list = await app.inject({
      method: 'GET',
      url: '/api/habits',
      headers: { 'x-telegram-init-data': auth },
    });
    const id = list.json().habits[0].id;
    const del = await app.inject({
      method: 'DELETE',
      url: `/api/habits/${id}`,
      headers: { 'x-telegram-init-data': auth },
    });
    expect(del.statusCode).toBe(200);
    expect(del.json().ok).toBe(true);
  });
});
