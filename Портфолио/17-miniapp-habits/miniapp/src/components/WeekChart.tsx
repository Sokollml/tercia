import type { OverallStats } from '../lib/types.js';

const WEEKDAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

/**
 * Недельный столбчатый график: доля выполненных привычек за каждый из 7 дней.
 * Высота столбца = count / total. Сегодняшний день подсвечен.
 */
export function WeekChart({ stats }: { stats: OverallStats }) {
  const todayIdx = stats.week.length - 1;
  const maxTotal = Math.max(1, stats.totalHabits);

  return (
    <div className="chart">
      <div className="chart__bars">
        {stats.week.map((d, i) => {
          const ratio = maxTotal === 0 ? 0 : d.count / maxTotal;
          const heightPct = Math.round(ratio * 100);
          return (
            <div className="chart__col" key={d.day}>
              <div className="chart__track">
                <div
                  className={`chart__fill${i === todayIdx ? ' chart__fill--today' : ''}`}
                  style={{ height: `${Math.max(heightPct, d.count > 0 ? 8 : 0)}%` }}
                  title={`${d.count} из ${d.total}`}
                />
              </div>
              <span className={`chart__label${i === todayIdx ? ' chart__label--today' : ''}`}>
                {WEEKDAY_LABELS[d.weekday]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
