import type { CardView } from '../lib/types.js';

/**
 * The visual loyalty card: a grid of stamp slots that fill up as the customer
 * collects stamps, plus the "N to reward" progress line.
 */
export function StampCard({ card }: { card: CardView }) {
  const slots = Array.from({ length: card.threshold }, (_, i) => i < card.stamps);
  const full = card.stamps === 0 && card.rewardsEarned > 0;

  return (
    <div className="stamp-card">
      <div className="stamp-card__header">
        <span className="stamp-card__brand">☕ Кофейня</span>
        <span className="stamp-card__count">
          {card.stamps}/{card.threshold}
        </span>
      </div>

      <div className="stamp-grid" role="list" aria-label="Штампы">
        {slots.map((filled, i) => (
          <div
            key={i}
            role="listitem"
            className={`stamp ${filled ? 'stamp--filled' : ''} ${
              i === card.threshold - 1 ? 'stamp--reward' : ''
            }`}
          >
            {i === card.threshold - 1 ? '🎁' : filled ? '★' : ''}
          </div>
        ))}
      </div>

      <div className="stamp-card__footer">
        {card.remaining === card.threshold && card.rewardsEarned > 0 ? (
          <p className="reward-line reward-line--ready">
            🎉 Награда получена! Начинаем новую карту.
          </p>
        ) : card.remaining === 1 ? (
          <p className="reward-line reward-line--close">
            Остался <b>1</b> штамп до бесплатного напитка!
          </p>
        ) : (
          <p className="reward-line">
            До награды: <b>{card.remaining}</b>{' '}
            {plural(card.remaining, 'штамп', 'штампа', 'штампов')}
          </p>
        )}
      </div>

      {full && <div className="stamp-card__ribbon">Свежая карта</div>}
    </div>
  );
}

function plural(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few;
  return many;
}
