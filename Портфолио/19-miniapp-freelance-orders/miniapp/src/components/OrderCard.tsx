import { Chip } from './Chip';
import { formatBudget, serviceLabel, timeAgo, urgencyLabel } from '../format';
import type { Order } from '../types';

interface OrderCardProps {
  order: Order;
  onOpen: (order: Order) => void;
}

const URGENCY_TONE = {
  low: 'default',
  medium: 'accent',
  high: 'danger',
} as const;

export function OrderCard({ order, onOpen }: OrderCardProps) {
  const responded = order.user_status === 'responded';
  const interested = order.user_status === 'interested';

  return (
    <button
      type="button"
      className={`card ${responded ? 'card--responded' : ''}`}
      onClick={() => onOpen(order)}
    >
      <div className="card__head">
        <span className="card__service">{serviceLabel(order.service_type)}</span>
        <span className="card__time">{timeAgo(order.created_at)}</span>
      </div>

      <p className="card__summary">
        {order.summary || order.raw_text.slice(0, 160)}
      </p>

      <div className="card__meta">
        <Chip tone="success">{formatBudget(order.budget)}</Chip>
        <Chip tone={URGENCY_TONE[order.urgency]}>{urgencyLabel(order.urgency)}</Chip>
        {interested && <Chip tone="accent">В избранном</Chip>}
        {responded && <Chip tone="success">Откликнулся</Chip>}
      </div>

      {order.skills_required.length > 0 && (
        <div className="card__skills">
          {order.skills_required.slice(0, 6).map((s) => (
            <span key={s} className="skill">
              {s}
            </span>
          ))}
        </div>
      )}

      <div className="card__foot">
        <span className="card__source">{order.source_chat}</span>
        {order.languages.length > 0 && (
          <span className="card__langs">{order.languages.join(' · ')}</span>
        )}
      </div>
    </button>
  );
}
