// Типы, зеркалирующие DTO бэкенда.

export interface WeekDayPoint {
  day: string; // YYYY-MM-DD
  done: boolean;
  weekday: number; // 0=Пн ... 6=Вс
}

export interface Habit {
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

export interface TgUser {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
}
