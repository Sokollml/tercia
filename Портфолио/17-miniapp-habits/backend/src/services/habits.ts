import type { Db } from '../db.js';
import type { TelegramUser } from '../auth/initData.js';
import {
  currentStreak,
  longestStreak,
  lastWeek,
  today,
  type WeekDayPoint,
} from './streak.js';

/**
 * Слой доступа к данным + вычисление статистики привычек.
 * Все функции работают через абстракцию Db (Postgres или SQLite) и
 * ВСЕГДА фильтруют по user_id — пользователь видит только свои привычки.
 */

// ── Строки из БД ──────────────────────────────────────────────────────────────
interface HabitRow {
  id: number;
  user_id: number;
  title: string;
  emoji: string;
  color: string;
  archived: boolean | number;
  created_at: string;
}

// ── DTO, отдаваемый фронтенду ────────────────────────────────────────────────
export interface HabitDTO {
  id: number;
  title: string;
  emoji: string;
  color: string;
  archived: boolean;
  createdAt: string;
  todayDone: boolean;
  currentStreak: number;
  longestStreak: number;
  totalCheckins: number;
  week: WeekDayPoint[];
}

export interface OverallStats {
  totalHabits: number;
  totalCheckins: number;
  bestStreak: number;
  doneToday: number;
  week: { day: string; weekday: number; count: number; total: number }[];
}

/** Создаёт пользователя, если его ещё нет, и обновляет профильные поля. */
export async function upsertUser(db: Db, user: TelegramUser): Promise<void> {
  // ON CONFLICT работает и в Postgres, и в современном SQLite (better-sqlite3).
  await db.query(
    `INSERT INTO users (id, username, first_name, last_name, language_code)
     VALUES ($1, $2, $3, $4, $5)
     ON CONFLICT (id) DO UPDATE SET
       username = EXCLUDED.username,
       first_name = EXCLUDED.first_name,
       last_name = EXCLUDED.last_name,
       language_code = EXCLUDED.language_code`,
    [
      user.id,
      user.username ?? null,
      user.first_name ?? null,
      user.last_name ?? null,
      user.language_code ?? null,
    ]
  );
}

function computeHabitDTO(row: HabitRow, days: string[]): HabitDTO {
  const todayStr = today();
  return {
    id: Number(row.id),
    title: row.title,
    emoji: row.emoji,
    color: row.color,
    archived: !!row.archived,
    createdAt: String(row.created_at),
    todayDone: days.includes(todayStr),
    currentStreak: currentStreak(days, todayStr),
    longestStreak: longestStreak(days),
    totalCheckins: new Set(days).size,
    week: lastWeek(days, todayStr),
  };
}

/** Список активных привычек пользователя со статистикой по каждой. */
export async function listHabits(db: Db, userId: number): Promise<HabitDTO[]> {
  const { rows: habits } = await db.query<HabitRow>(
    `SELECT * FROM habits WHERE user_id = $1 AND archived = FALSE ORDER BY created_at ASC, id ASC`,
    [userId]
  );
  if (habits.length === 0) return [];

  // Одним запросом достаём все отметки этих привычек и группируем в памяти.
  const ids = habits.map((h) => h.id);
  const placeholders = ids.map((_, i) => `$${i + 1}`).join(', ');
  const { rows: checkins } = await db.query<{ habit_id: number; day: string }>(
    `SELECT habit_id, day FROM checkins WHERE habit_id IN (${placeholders})`,
    ids
  );

  const byHabit = new Map<number, string[]>();
  for (const c of checkins) {
    const key = Number(c.habit_id);
    if (!byHabit.has(key)) byHabit.set(key, []);
    byHabit.get(key)!.push(c.day);
  }

  return habits.map((h) => computeHabitDTO(h, byHabit.get(Number(h.id)) ?? []));
}

async function getHabitOwned(
  db: Db,
  userId: number,
  habitId: number
): Promise<HabitRow | null> {
  const { rows } = await db.query<HabitRow>(
    `SELECT * FROM habits WHERE id = $1 AND user_id = $2`,
    [habitId, userId]
  );
  return rows[0] ?? null;
}

async function habitDTO(db: Db, row: HabitRow): Promise<HabitDTO> {
  const { rows } = await db.query<{ day: string }>(
    `SELECT day FROM checkins WHERE habit_id = $1`,
    [row.id]
  );
  return computeHabitDTO(row, rows.map((r) => r.day));
}

export interface CreateHabitInput {
  title: string;
  emoji?: string;
  color?: string;
}

export async function createHabit(
  db: Db,
  userId: number,
  input: CreateHabitInput
): Promise<HabitDTO> {
  const { rows } = await db.query<HabitRow>(
    `INSERT INTO habits (user_id, title, emoji, color)
     VALUES ($1, $2, $3, $4)
     RETURNING *`,
    [userId, input.title, input.emoji || '✅', input.color || '#6C5CE7']
  );
  return habitDTO(db, rows[0]);
}

export interface UpdateHabitInput {
  title?: string;
  emoji?: string;
  color?: string;
  archived?: boolean;
}

export async function updateHabit(
  db: Db,
  userId: number,
  habitId: number,
  input: UpdateHabitInput
): Promise<HabitDTO | null> {
  const existing = await getHabitOwned(db, userId, habitId);
  if (!existing) return null;

  const title = input.title ?? existing.title;
  const emoji = input.emoji ?? existing.emoji;
  const color = input.color ?? existing.color;
  const archived = input.archived ?? !!existing.archived;

  const { rows } = await db.query<HabitRow>(
    `UPDATE habits SET title = $1, emoji = $2, color = $3, archived = $4
     WHERE id = $5 AND user_id = $6
     RETURNING *`,
    [title, emoji, color, archived, habitId, userId]
  );
  return habitDTO(db, rows[0]);
}

export async function deleteHabit(
  db: Db,
  userId: number,
  habitId: number
): Promise<boolean> {
  const existing = await getHabitOwned(db, userId, habitId);
  if (!existing) return false;
  await db.query(`DELETE FROM habits WHERE id = $1 AND user_id = $2`, [
    habitId,
    userId,
  ]);
  return true;
}

/**
 * Переключает отметку выполнения привычки за указанный день (по умолчанию —
 * сегодня). Если отметка была — снимаем, если не было — ставим. Возвращает
 * обновлённый DTO привычки или null, если привычка не принадлежит пользователю.
 */
export async function toggleCheckin(
  db: Db,
  userId: number,
  habitId: number,
  day: string
): Promise<HabitDTO | null> {
  const habit = await getHabitOwned(db, userId, habitId);
  if (!habit) return null;

  const { rows } = await db.query<{ id: number }>(
    `SELECT id FROM checkins WHERE habit_id = $1 AND day = $2`,
    [habitId, day]
  );

  if (rows.length > 0) {
    await db.query(`DELETE FROM checkins WHERE habit_id = $1 AND day = $2`, [
      habitId,
      day,
    ]);
  } else {
    await db.query(`INSERT INTO checkins (habit_id, day) VALUES ($1, $2)`, [
      habitId,
      day,
    ]);
  }

  return habitDTO(db, habit);
}

/** Сводная статистика по всем активным привычкам пользователя. */
export async function getStats(db: Db, userId: number): Promise<OverallStats> {
  const habits = await listHabits(db, userId);
  const totalHabits = habits.length;
  const totalCheckins = habits.reduce((s, h) => s + h.totalCheckins, 0);
  const bestStreak = habits.reduce((m, h) => Math.max(m, h.longestStreak), 0);
  const doneToday = habits.filter((h) => h.todayDone).length;

  // Недельный график: сколько привычек выполнено в каждый из последних 7 дней.
  const template = lastWeek([], today());
  const week = template.map((pt) => {
    const count = habits.filter((h) =>
      h.week.some((w) => w.day === pt.day && w.done)
    ).length;
    return { day: pt.day, weekday: pt.weekday, count, total: totalHabits };
  });

  return { totalHabits, totalCheckins, bestStreak, doneToday, week };
}
