import { useCallback, useEffect, useRef, useState } from 'react';
import { FeedScreen } from './screens/FeedScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { OrderScreen } from './screens/OrderScreen';
import { useTelegram } from './hooks/useTelegram';
import { getSettings } from './api';
import type { Order, UserSettings } from './types';
import { EMPTY_SETTINGS } from './types';

type Tab = 'feed' | 'settings';

export function App() {
  const tg = useTelegram();
  const [tab, setTab] = useState<Tab>('feed');
  const [settings, setSettings] = useState<UserSettings>(EMPTY_SETTINGS);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Order | null>(null);

  // reload-функцию ленты регистрирует FeedScreen — дёргаем после смены статуса.
  const reloadFeedRef = useRef<() => void>(() => {});
  const registerReload = useCallback((fn: () => void) => {
    reloadFeedRef.current = fn;
  }, []);

  // Первичная загрузка настроек пользователя.
  useEffect(() => {
    let alive = true;
    getSettings()
      .then((s) => {
        if (alive) setSettings(s);
      })
      .catch((e: unknown) => {
        if (alive) {
          setSettingsError(e instanceof Error ? e.message : 'Ошибка настроек');
        }
      });
    return () => {
      alive = false;
    };
  }, []);

  const openOrder = useCallback(
    (order: Order) => {
      tg.haptic('light');
      setSelected(order);
    },
    [tg],
  );

  // После изменения статуса/заметки в карточке — обновляем ленту.
  const onOrderChanged = useCallback((updated: Order) => {
    setSelected(updated);
    reloadFeedRef.current();
  }, []);

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">Фриланс-заказы</h1>
        {tg.userName && <span className="app__user">{tg.userName}</span>}
      </header>

      {settingsError && tab === 'settings' && (
        <div className="notice notice--error">{settingsError}</div>
      )}

      <main className="app__body">
        {tab === 'feed' ? (
          <FeedScreen
            settings={settings}
            onOpenOrder={openOrder}
            registerReload={registerReload}
          />
        ) : (
          <SettingsScreen
            settings={settings}
            onSaved={setSettings}
            haptic={tg.haptic}
          />
        )}
      </main>

      <nav className="tabbar">
        <button
          type="button"
          className={`tabbar__btn ${tab === 'feed' ? 'tabbar__btn--active' : ''}`}
          onClick={() => setTab('feed')}
        >
          <span className="tabbar__icon">🗂️</span>
          Лента
        </button>
        <button
          type="button"
          className={`tabbar__btn ${tab === 'settings' ? 'tabbar__btn--active' : ''}`}
          onClick={() => setTab('settings')}
        >
          <span className="tabbar__icon">⚙️</span>
          Настройки
        </button>
      </nav>

      {selected && (
        <OrderScreen
          order={selected}
          onClose={() => setSelected(null)}
          onChanged={onOrderChanged}
          openLink={tg.openLink}
          haptic={tg.haptic}
        />
      )}
    </div>
  );
}
