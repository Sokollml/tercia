import { useState } from 'react';
import { Chip } from '../components/Chip';
import { setOrderStatus } from '../api';
import { formatBudget, serviceLabel, timeAgo, urgencyLabel } from '../format';
import type { Order, OrderUserStatus } from '../types';

interface OrderScreenProps {
  order: Order;
  onClose: () => void;
  onChanged: (order: Order) => void;
  openLink: (url: string) => void;
  haptic: (style?: 'light' | 'medium' | 'heavy') => void;
}

const STATUS_OPTIONS: { key: OrderUserStatus; label: string }[] = [
  { key: 'new', label: 'Новый' },
  { key: 'interested', label: 'В избранное' },
  { key: 'responded', label: 'Откликнулся' },
  { key: 'hidden', label: 'Скрыть' },
];

/**
 * Карточка заказа. «Открыть в Telegram» — deep-link на исходное сообщение
 * (отклик пишет САМ пользователь). Плюс статус и личная заметка.
 */
export function OrderScreen({ order, onClose, onChanged, openLink, haptic }: OrderScreenProps) {
  const [status, setStatus] = useState<OrderUserStatus>(order.user_status);
  const [note, setNote] = useState(order.user_note ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Deep-link: приоритет — прямая ссылка на сообщение, иначе профиль автора.
  const tgLink =
    order.message_link ||
    (order.author_username ? `https://t.me/${order.author_username}` : null);

  async function persist(nextStatus: OrderUserStatus, nextNote: string) {
    setSaving(true);
    setError(null);
    try {
      await setOrderStatus(order.id, nextStatus, nextNote || null);
      onChanged({ ...order, user_status: nextStatus, user_note: nextNote || null });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Не удалось сохранить');
    } finally {
      setSaving(false);
    }
  }

  function chooseStatus(next: OrderUserStatus) {
    haptic('light');
    setStatus(next);
    void persist(next, note);
  }

  function openTelegram() {
    if (!tgLink) return;
    haptic('medium');
    // Помечаем «откликнулся» — сам отклик пользователь пишет в Telegram.
    if (status !== 'responded') {
      setStatus('responded');
      void persist('responded', note);
    }
    openLink(tgLink);
  }

  return (
    <div className="modal" role="dialog" aria-modal="true">
      <div className="modal__backdrop" onClick={onClose} />
      <div className="modal__sheet">
        <div className="modal__grip" />

        <div className="modal__head">
          <div className="modal__badges">
            <Chip tone="success">{formatBudget(order.budget)}</Chip>
            <Chip tone={order.urgency === 'high' ? 'danger' : 'accent'}>
              {urgencyLabel(order.urgency)}
            </Chip>
            <Chip>{serviceLabel(order.service_type)}</Chip>
          </div>
          <button type="button" className="modal__close" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>

        {order.summary && <p className="modal__summary">{order.summary}</p>}

        <div className="modal__text">{order.raw_text}</div>

        {order.skills_required.length > 0 && (
          <div className="card__skills">
            {order.skills_required.map((s) => (
              <span key={s} className="skill">
                {s}
              </span>
            ))}
          </div>
        )}

        <div className="modal__info">
          <span>{order.source_chat}</span>
          {order.author_username && <span>@{order.author_username}</span>}
          <span>{timeAgo(order.created_at)}</span>
          {order.languages.length > 0 && <span>{order.languages.join(' · ')}</span>}
        </div>

        <button
          type="button"
          className="btn btn--primary btn--block"
          disabled={!tgLink}
          onClick={openTelegram}
        >
          {tgLink ? 'Открыть в Telegram' : 'Ссылка недоступна'}
        </button>

        <div className="field">
          <label className="field__label">Статус</label>
          <div className="chips">
            {STATUS_OPTIONS.map((o) => (
              <Chip
                key={o.key}
                tone="accent"
                active={status === o.key}
                onClick={() => chooseStatus(o.key)}
              >
                {o.label}
              </Chip>
            ))}
          </div>
        </div>

        <div className="field">
          <label className="field__label" htmlFor="note">
            Заметка
          </label>
          <textarea
            id="note"
            className="input input--area"
            rows={3}
            value={note}
            placeholder="Например: написал(а), жду ответа"
            onChange={(e) => setNote(e.target.value)}
            onBlur={() => {
              if ((order.user_note ?? '') !== note) void persist(status, note);
            }}
          />
        </div>

        {error && <div className="notice notice--error">{error}</div>}
        {saving && <div className="loader">Сохранение…</div>}
      </div>
    </div>
  );
}
