import { getInitData } from './telegram.js';
import type { Habit, OverallStats } from './types.js';

/**
 * Тонкий клиент REST API. К КАЖДОМУ запросу добавляем заголовок
 * X-Telegram-Init-Data — бэкенд по нему проверяет подпись и авторизует.
 */

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Telegram-Init-Data': getInitData(),
      ...(init.headers || {}),
    },
  });

  if (!res.ok) {
    let msg = `Ошибка ${res.status}`;
    try {
      const body = await res.json();
      if (body?.error) msg = body.error;
    } catch {
      /* тело не JSON */
    }
    throw new ApiError(res.status, msg);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listHabits: () =>
    request<{ habits: Habit[] }>('/api/habits').then((r) => r.habits),

  createHabit: (input: { title: string; emoji: string; color: string }) =>
    request<{ habit: Habit }>('/api/habits', {
      method: 'POST',
      body: JSON.stringify(input),
    }).then((r) => r.habit),

  updateHabit: (
    id: number,
    input: Partial<{ title: string; emoji: string; color: string; archived: boolean }>
  ) =>
    request<{ habit: Habit }>(`/api/habits/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    }).then((r) => r.habit),

  deleteHabit: (id: number) =>
    request<{ ok: boolean }>(`/api/habits/${id}`, { method: 'DELETE' }),

  toggle: (id: number, day?: string) =>
    request<{ habit: Habit }>(`/api/habits/${id}/toggle`, {
      method: 'POST',
      body: JSON.stringify(day ? { day } : {}),
    }).then((r) => r.habit),

  stats: () => request<{ stats: OverallStats }>('/api/stats').then((r) => r.stats),
};
