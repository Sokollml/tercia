import { describe, it, expect } from 'vitest';
import {
  currentStreak,
  longestStreak,
  lastWeek,
  addDays,
} from '../src/services/streak.js';

const TODAY = '2026-08-02';

describe('currentStreak', () => {
  it('0 без отметок', () => {
    expect(currentStreak([], TODAY)).toBe(0);
  });

  it('считает цепочку, заканчивающуюся сегодня', () => {
    const days = [TODAY, addDays(TODAY, -1), addDays(TODAY, -2)];
    expect(currentStreak(days, TODAY)).toBe(3);
  });

  it('засчитывает живой стрик, если последняя отметка вчера', () => {
    const days = [addDays(TODAY, -1), addDays(TODAY, -2)];
    expect(currentStreak(days, TODAY)).toBe(2);
  });

  it('обнуляется при разрыве (последняя отметка позавчера)', () => {
    const days = [addDays(TODAY, -2), addDays(TODAY, -3)];
    expect(currentStreak(days, TODAY)).toBe(0);
  });

  it('игнорирует дубликаты дней', () => {
    const days = [TODAY, TODAY, addDays(TODAY, -1)];
    expect(currentStreak(days, TODAY)).toBe(2);
  });
});

describe('longestStreak', () => {
  it('находит самую длинную цепочку в истории', () => {
    const days = [
      '2026-07-01',
      '2026-07-02',
      '2026-07-03', // цепочка 3
      '2026-07-10',
      '2026-07-11', // цепочка 2
    ];
    expect(longestStreak(days)).toBe(3);
  });

  it('1 для единственной отметки', () => {
    expect(longestStreak(['2026-07-01'])).toBe(1);
  });
});

describe('lastWeek', () => {
  it('возвращает ровно 7 дней от старого к новому, последний — сегодня', () => {
    const week = lastWeek([TODAY], TODAY);
    expect(week).toHaveLength(7);
    expect(week[6].day).toBe(TODAY);
    expect(week[6].done).toBe(true);
    expect(week[0].done).toBe(false);
  });
});
