import type { OverallStats } from '../lib/types.js';

export function StatsBar({ stats }: { stats: OverallStats }) {
  const items = [
    { label: 'Сегодня', value: `${stats.doneToday}/${stats.totalHabits}` },
    { label: 'Отметок', value: stats.totalCheckins },
    { label: 'Рекорд', value: `${stats.bestStreak} 🔥` },
  ];
  return (
    <div className="statsbar">
      {items.map((it) => (
        <div className="statsbar__item" key={it.label}>
          <div className="statsbar__value">{it.value}</div>
          <div className="statsbar__label">{it.label}</div>
        </div>
      ))}
    </div>
  );
}
