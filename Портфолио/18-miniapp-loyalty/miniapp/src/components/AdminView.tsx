import { useEffect, useState } from 'react';
import { ApiError, getStats, grantStamp } from '../lib/api.js';
import type { GrantStampResponse, MeResponse, StatsResponse } from '../lib/types.js';
import { haptic, impact, scanQr } from '../lib/telegram.js';

/**
 * Admin (cafe staff) screen: scan a customer's QR or type their code, grant a
 * single stamp, and see live cafe statistics. The backend enforces that only
 * admins can reach these endpoints — this UI is only shown to admins.
 */
export function AdminView({ me }: { me: MeResponse }) {
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<GrantStampResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  async function refreshStats() {
    try {
      setStats(await getStats());
    } catch {
      /* stats are non-critical */
    }
  }

  useEffect(() => {
    void refreshStats();
  }, []);

  async function submit(rawCode: string) {
    const clean = rawCode.trim();
    if (!clean || busy) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      // A fresh idempotency key per deliberate action. If the backend receives
      // the same key twice (double tap / retry) it will not double-count.
      const key = cryptoRandomId();
      const res = await grantStamp(clean, key);
      setResult(res);
      setCode('');
      haptic(res.rewardGranted ? 'success' : 'success');
      void refreshStats();
    } catch (err) {
      haptic('error');
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleScan() {
    impact('medium');
    try {
      const scanned = await scanQr();
      if (scanned) await submit(scanned);
    } catch {
      setError('Сканер недоступен в этой версии Telegram. Введите код вручную.');
    }
  }

  return (
    <div className="screen">
      <header className="greeting">
        <h1>Панель бариста</h1>
        <p className="muted">{me.user.firstName ?? 'Сотрудник'} · выдача штампов</p>
      </header>

      <section className="admin-actions">
        <button className="primary-btn" onClick={handleScan} disabled={busy}>
          📷 Сканировать QR гостя
        </button>

        <div className="divider"><span>или</span></div>

        <form
          className="code-form"
          onSubmit={(e) => {
            e.preventDefault();
            void submit(code);
          }}
        >
          <input
            className="code-input"
            inputMode="text"
            autoCapitalize="characters"
            placeholder="LOY-XXXX-XXXX"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            disabled={busy}
          />
          <button className="secondary-btn" type="submit" disabled={busy || !code.trim()}>
            {busy ? '…' : 'Штамп'}
          </button>
        </form>
      </section>

      {error && <div className="banner banner--error">{error}</div>}

      {result && <ResultCard result={result} />}

      <section className="stats">
        <h2 className="stats__title">Статистика</h2>
        {stats ? (
          <div className="stats__grid">
            <Stat label="Гостей" value={stats.totalCustomers} />
            <Stat label="Штампов сегодня" value={stats.stampsToday} />
            <Stat label="Штампов всего" value={stats.totalStamps} />
            <Stat label="Наград выдано" value={stats.rewardsEarned} />
            <Stat label="Активных карт" value={stats.activeCards} />
          </div>
        ) : (
          <div className="stats__grid stats__grid--skeleton">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="stat stat--skeleton" />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function ResultCard({ result }: { result: GrantStampResponse }) {
  const name = result.customer.firstName ?? result.customer.username ?? 'Гость';
  if (result.alreadyApplied) {
    return (
      <div className="banner banner--warn">
        Этот штамп уже был начислен ранее (повторное сканирование). Карта: {result.card.stamps}/
        {result.card.threshold}.
      </div>
    );
  }
  if (result.rewardGranted) {
    return (
      <div className="result result--reward">
        <div className="result__emoji">🎁</div>
        <div className="result__title">Награда для {name}!</div>
        <div className="result__sub">Выдайте бесплатный напиток. Карта обнулена.</div>
      </div>
    );
  }
  return (
    <div className="result result--ok">
      <div className="result__emoji">✅</div>
      <div className="result__title">Штамп начислен</div>
      <div className="result__sub">
        {name}: {result.card.stamps}/{result.card.threshold} · до награды {result.card.remaining}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="stat">
      <span className="stat__value">{value}</span>
      <span className="stat__label">{label}</span>
    </div>
  );
}

function cryptoRandomId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) {
    switch (err.code) {
      case 'card_not_found':
        return 'Карта с таким кодом не найдена.';
      case 'admin_only':
      case 'forbidden':
        return 'Недостаточно прав для начисления штампа.';
      case 'empty_code':
        return 'Введите код карты.';
      default:
        return `Ошибка: ${err.code}`;
    }
  }
  return 'Не удалось связаться с сервером.';
}
