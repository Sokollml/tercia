/**
 * Работа с датами и расчёт стриков.
 *
 * Даты храним и передаём как строки формата "YYYY-MM-DD" (локальная дата дня).
 * Чтобы избежать ошибок часовых поясов, всю арифметику делаем в UTC на основе
 * этих строк.
 */

/** Строка YYYY-MM-DD из Date (в UTC). */
export function toDayString(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** Парсит "YYYY-MM-DD" в timestamp полуночи UTC. */
function dayToUtc(day: string): number {
  const [y, m, d] = day.split('-').map(Number);
  return Date.UTC(y, m - 1, d);
}

const DAY_MS = 86_400_000;

/** Сегодняшний день (UTC) строкой. */
export function today(now: Date = new Date()): string {
  return toDayString(now);
}

/** day + n дней, строкой. n может быть отрицательным. */
export function addDays(day: string, n: number): string {
  return toDayString(new Date(dayToUtc(day) + n * DAY_MS));
}

/** Разница в днях (a - b). */
export function diffDays(a: string, b: string): number {
  return Math.round((dayToUtc(a) - dayToUtc(b)) / DAY_MS);
}

/**
 * Текущий стрик — число подряд идущих дней с отметкой, заканчивающихся сегодня
 * ИЛИ вчера. Если последняя отметка была раньше, чем вчера, стрик = 0
 * (цепочка прервана). Отметка сегодня продолжает стрик; отметка только вчера
 * тоже засчитывается как «живой» стрик (день ещё не закончился).
 *
 * @param days     список дат-отметок (строки YYYY-MM-DD), возможны дубликаты
 * @param todayStr текущий день (для тестируемости)
 */
export function currentStreak(days: string[], todayStr: string = today()): number {
  if (days.length === 0) return 0;
  const set = new Set(days);

  // Определяем «якорь»: сегодня, если есть отметка сегодня, иначе вчера.
  const yesterday = addDays(todayStr, -1);
  let cursor: string;
  if (set.has(todayStr)) {
    cursor = todayStr;
  } else if (set.has(yesterday)) {
    cursor = yesterday;
  } else {
    return 0;
  }

  // Идём назад, пока встречаем отметки без разрывов.
  let streak = 0;
  while (set.has(cursor)) {
    streak += 1;
    cursor = addDays(cursor, -1);
  }
  return streak;
}

/**
 * Самый длинный стрик за всю историю отметок.
 */
export function longestStreak(days: string[]): number {
  if (days.length === 0) return 0;
  const unique = Array.from(new Set(days)).sort(); // по возрастанию
  let best = 1;
  let run = 1;
  for (let i = 1; i < unique.length; i++) {
    if (diffDays(unique[i], unique[i - 1]) === 1) {
      run += 1;
    } else {
      run = 1;
    }
    if (run > best) best = run;
  }
  return best;
}

/**
 * Данные для недельного графика: последние 7 дней (включая сегодня),
 * от старого к новому. Для каждого дня — была ли отметка.
 */
export interface WeekDayPoint {
  day: string;
  done: boolean;
  weekday: number; // 0=Пн ... 6=Вс
}

export function lastWeek(days: string[], todayStr: string = today()): WeekDayPoint[] {
  const set = new Set(days);
  const points: WeekDayPoint[] = [];
  for (let i = 6; i >= 0; i--) {
    const day = addDays(todayStr, -i);
    // JS getUTCDay: 0=Вс..6=Сб. Переводим в 0=Пн..6=Вс.
    const jsDow = new Date(dayToUtc(day)).getUTCDay();
    const weekday = (jsDow + 6) % 7;
    points.push({ day, done: set.has(day), weekday });
  }
  return points;
}
