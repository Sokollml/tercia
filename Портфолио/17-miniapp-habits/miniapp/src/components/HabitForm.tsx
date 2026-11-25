import { useEffect, useState } from 'react';
import type { Habit } from '../lib/types.js';
import { hapticImpact } from '../lib/telegram.js';

const EMOJIS = ['✅', '💧', '🏃', '📚', '🧘', '🥗', '💪', '😴', '🚭', '🧠', '🎯', '✍️'];
const COLORS = ['#6C5CE7', '#00B894', '#0984E3', '#E17055', '#E84393', '#FDCB6E', '#00CEC9', '#D63031'];

export interface HabitDraft {
  title: string;
  emoji: string;
  color: string;
}

interface Props {
  initial?: Habit | null;
  submitting?: boolean;
  onSubmit: (draft: HabitDraft) => void;
  onChange?: (draft: HabitDraft) => void;
  onDelete?: () => void;
  onClose: () => void;
}

/**
 * Модальная форма создания/редактирования привычки (bottom sheet).
 * Форма управляет только полями; отправку инициирует MainButton из App,
 * поэтому наружу отдаётся текущий draft через onSubmit по нажатию кнопки.
 */
export function HabitForm({ initial, submitting, onSubmit, onChange, onDelete, onClose }: Props) {
  const [title, setTitle] = useState(initial?.title ?? '');
  const [emoji, setEmoji] = useState(initial?.emoji ?? EMOJIS[0]);
  const [color, setColor] = useState(initial?.color ?? COLORS[0]);

  useEffect(() => {
    // Небольшая тактильная отдача при открытии.
    hapticImpact('light');
  }, []);

  // Сообщаем родителю актуальный черновик — чтобы нативный MainButton Telegram
  // отправлял именно текущие значения полей, а не те, что были при открытии.
  useEffect(() => {
    onChange?.({ title: title.trim(), emoji, color });
  }, [title, emoji, color, onChange]);

  const isEdit = !!initial;
  const canSubmit = title.trim().length > 0 && !submitting;

  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <div
        className="sheet"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        style={{ ['--accent' as string]: color }}
      >
        <div className="sheet__handle" />
        <h2 className="sheet__title">
          {isEdit ? 'Редактировать привычку' : 'Новая привычка'}
        </h2>

        <label className="field">
          <span className="field__label">Название</span>
          <input
            className="field__input"
            value={title}
            maxLength={80}
            placeholder="Например, «Читать 20 минут»"
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </label>

        <div className="field">
          <span className="field__label">Иконка</span>
          <div className="picker">
            {EMOJIS.map((e) => (
              <button
                key={e}
                type="button"
                className={`picker__emoji${e === emoji ? ' picker__emoji--active' : ''}`}
                onClick={() => {
                  setEmoji(e);
                  hapticImpact('light');
                }}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <span className="field__label">Цвет</span>
          <div className="picker">
            {COLORS.map((c) => (
              <button
                key={c}
                type="button"
                className={`picker__color${c === color ? ' picker__color--active' : ''}`}
                style={{ background: c }}
                aria-label={`Цвет ${c}`}
                onClick={() => {
                  setColor(c);
                  hapticImpact('light');
                }}
              />
            ))}
          </div>
        </div>

        {/* Кнопка отправки в самой форме — дублирует MainButton для браузера. */}
        <button
          className="btn btn--primary btn--block"
          disabled={!canSubmit}
          onClick={() => onSubmit({ title: title.trim(), emoji, color })}
        >
          {isEdit ? 'Сохранить' : 'Создать привычку'}
        </button>

        {isEdit && onDelete && (
          <button className="btn btn--danger btn--block" onClick={onDelete}>
            Удалить привычку
          </button>
        )}
      </div>
    </div>
  );
}
