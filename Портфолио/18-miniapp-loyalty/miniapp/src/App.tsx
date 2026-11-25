import { useCallback, useEffect, useState } from 'react';
import { ApiError, getMe } from './lib/api.js';
import type { MeResponse } from './lib/types.js';
import { ClientView } from './components/ClientView.js';
import { AdminView } from './components/AdminView.js';

type State =
  | { phase: 'loading' }
  | { phase: 'error'; message: string }
  | { phase: 'ready'; me: MeResponse };

/**
 * Root component. Loads identity from the backend (which derives the role from
 * the verified initData) and routes to the customer or admin experience.
 */
export default function App() {
  const [state, setState] = useState<State>({ phase: 'loading' });

  const load = useCallback(async () => {
    setState({ phase: 'loading' });
    try {
      const me = await getMe();
      setState({ phase: 'ready', me });
    } catch (err) {
      setState({ phase: 'error', message: describe(err) });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state.phase === 'loading') {
    return (
      <div className="center-screen">
        <div className="spinner" aria-label="Загрузка" />
        <p className="muted">Загружаем вашу карту…</p>
      </div>
    );
  }

  if (state.phase === 'error') {
    return (
      <div className="center-screen">
        <div className="empty-emoji">🥲</div>
        <h2>Не удалось открыть карту</h2>
        <p className="muted">{state.message}</p>
        <button className="primary-btn" onClick={() => void load()}>
          Повторить
        </button>
      </div>
    );
  }

  return state.me.role === 'admin' ? (
    <AdminView me={state.me} />
  ) : (
    <ClientView me={state.me} onRefresh={() => void load()} />
  );
}

function describe(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 401) {
      return 'Откройте приложение из Telegram — данные авторизации не найдены.';
    }
    return `Ошибка сервера (${err.code}).`;
  }
  return 'Проверьте подключение к интернету и попробуйте снова.';
}
