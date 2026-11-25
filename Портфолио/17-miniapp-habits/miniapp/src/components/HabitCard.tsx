import type { Habit } from '../lib/types.js';

const WEEKDAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

interface Props {
  habit: Habit;
  busy?: boolean;
  onToggle: (habit: Habit) => void;
  onEdit: (habit: Habit) => void;
}

/**
 * Карточка привычки: эмодзи + название, стрик, недельная «полоска» из 7 точек и
 * большая кнопка отметки за сегодня. Основной акцент карточки красится в цвет
 * привычки.
 */
export function HabitCard({ habit, busy, onToggle, onEdit }: Props) {
  return (
    <article
      className="card"
      style={{ ['--accent' as string]: habit.color }}
    >
      <div className="card__main">
        <button
          className="card__info"
          onClick={() => onEdit(habit)}
          aria-label={`Изменить привычку ${habit.title}`}
        >
          <span className="card__emoji">{habit.emoji}</span>
          <span className="card__texts">
            <span className="card__title">{habit.title}</span>
            <span className="card__meta">
              {habit.currentStreak > 0 ? (
                <span className="card__streak">🔥 {habit.currentStreak} дн.</span>
              ) : (
                <span className="card__streak card__streak--muted">Начни серию</span>
              )}
              <span className="card__dot">·</span>
              <span>рекорд {habit.longestStreak}</span>
            </span>
          </span>
        </button>

        <button
          className={`check${habit.todayDone ? ' check--done' : ''}`}
          onClick={() => onToggle(habit)}
          disabled={busy}
          aria-pressed={habit.todayDone}
          aria-label={habit.todayDone ? 'Снять отметку за сегодня' : 'Отметить сегодня'}
        >
          <span className="check__icon">{habit.todayDone ? '✓' : ''}</span>
        </button>
      </div>

      <div className="week" aria-label="Последние 7 дней">
        {habit.week.map((d) => (
          <div className="week__cell" key={d.day} title={d.day}>
            <span
              className={`week__dot${d.done ? ' week__dot--done' : ''}`}
              aria-hidden="true"
            />
            <span className="week__label">{WEEKDAY_LABELS[d.weekday]}</span>
          </div>
        ))}
      </div>
    </article>
  );
}
