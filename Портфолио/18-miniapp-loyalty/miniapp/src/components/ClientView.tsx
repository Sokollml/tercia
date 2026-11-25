import { useState } from 'react';
import type { MeResponse } from '../lib/types.js';
import { QrCode } from './QrCode.js';
import { StampCard } from './StampCard.js';
import { impact } from '../lib/telegram.js';

/**
 * Customer screen: shows the loyalty card, the QR/manual code the cashier
 * scans, and lifetime rewards. Read-only — customers can never add stamps.
 */
export function ClientView({ me, onRefresh }: { me: MeResponse; onRefresh: () => void }) {
  const [showCode, setShowCode] = useState(false);
  const { card, user } = me;

  return (
    <div className="screen">
      <header className="greeting">
        <h1>Привет, {user.firstName ?? 'гость'} 👋</h1>
        <p className="muted">Собирайте штампы — каждый {card.threshold}-й напиток бесплатно.</p>
      </header>

      <StampCard card={card} />

      <section className="qr-block">
        <p className="qr-block__hint">Покажите этот код бариста, чтобы получить штамп</p>
        <div className="qr-frame">
          <QrCode value={card.code} />
        </div>
        <button
          className="link-btn"
          onClick={() => {
            impact('light');
            setShowCode((v) => !v);
          }}
        >
          {showCode ? 'Скрыть код' : 'Показать код цифрами'}
        </button>
        {showCode && <div className="card-code">{card.code}</div>}
      </section>

      <section className="lifetime">
        <div className="lifetime__item">
          <span className="lifetime__num">{card.rewardsEarned}</span>
          <span className="lifetime__label">наград всего</span>
        </div>
        <div className="lifetime__item">
          <span className="lifetime__num">{card.stamps}</span>
          <span className="lifetime__label">штампов сейчас</span>
        </div>
      </section>

      <button className="ghost-btn" onClick={onRefresh}>
        Обновить
      </button>
    </div>
  );
}
