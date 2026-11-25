import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError } from './lib/api.js';
import type { Habit, OverallStats } from './lib/types.js';
import {
  getInitData,
  hapticImpact,
  hapticNotification,
  hideBackButton,
  hideMainButton,
  setMainButtonLoading,
  showBackButton,
  showMainButton,
} from './lib/telegram.js';
import { HabitCard } from './components/HabitCard.js';
import { HabitForm, type HabitDraft } from './components/HabitForm.js';
import { WeekChart } from './components/WeekChart.js';
import { StatsBar } from './components/StatsBar.js';
import { EmptyState } from './components/EmptyState.js';
import { Loader } from './components/Loader.js';

type Editing = { mode: 'create' } | { mode: 'edit'; habit: Habit } | null;

export default function App() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [stats, setStats] = useState<OverallStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Editing>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Черновик формы держим в ref, чтобы MainButton всегда читал актуальные значения.
  const draftRef = useRef<HabitDraft | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [h, s] = await Promise.all([api.listHabits(), api.stats()]);
      setHabits(h);
      setStats(s);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Не удалось загрузить данные';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  // Переключение отметки за сегодня с оптимистичным обновлением.
  const onToggle = useCallback(
    async (habit: Habit) => {
      setBusyId(habit.id);
      hapticImpact('medium');
      try {
        const updated = await api.toggle(habit.id);
        setHabits((prev) => prev.map((h) => (h.id === updated.id ? updated : h)));
        hapticNotification(updated.todayDone ? 'success' : 'warning');
        // Обновляем сводку (стрики/график) в фоне.
        api.stats().then(setStats).catch(() => {});
      } catch (e) {
        const msg = e instanceof ApiError ? e.message : 'Ошибка отметки';
        setError(msg);
        hapticNotification('error');
      } finally {
        setBusyId(null);
      }
    },
    []
  );

  const submitDraft = useCallback(async () => {
    const draft = draftRef.current;
    if (!draft || !draft.title.trim()) return;
    setSubmitting(true);
    setMainButtonLoading(true);
    try {
      if (editing?.mode === 'edit') {
        const updated = await api.updateHabit(editing.habit.id, draft);
        setHabits((prev) => prev.map((h) => (h.id === updated.id ? updated : h)));
      } else {
        const created = await api.createHabit(draft);
        setHabits((prev) => [...prev, created]);
      }
      hapticNotification('success');
      setEditing(null);
      api.stats().then(setStats).catch(() => {});
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Не удалось сохранить';
      setError(msg);
      hapticNotification('error');
    } finally {
      setSubmitting(false);
      setMainButtonLoading(false);
    }
  }, [editing]);

  const onDelete = useCallback(async () => {
    if (editing?.mode !== 'edit') return;
    const id = editing.habit.id;
    setSubmitting(true);
    try {
      await api.deleteHabit(id);
      setHabits((prev) => prev.filter((h) => h.id !== id));
      hapticNotification('success');
      setEditing(null);
      api.stats().then(setStats).catch(() => {});
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Не удалось удалить';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }, [editing]);

  // Управление нативными кнопками Telegram в зависимости от экрана.
  useEffect(() => {
    if (editing) {
      showBackButton(() => setEditing(null));
      showMainButton(editing.mode === 'edit' ? 'Сохранить' : 'Создать привычку', () => {
        void submitDraft();
      });
    } else {
      hideBackButton();
      showMainButton('Добавить привычку', () => {
        draftRef.current = null;
        setEditing({ mode: 'create' });
      });
    }
    return () => {
      // очистка не требуется — кнопки переустанавливаются на каждом переходе
    };
  }, [editing, submitDraft]);

  useEffect(() => {
    return () => {
      hideMainButton();
      hideBackButton();
    };
  }, []);

  // Нет initData — приложение открыто вне Telegram.
  if (!getInitData()) {
    return (
      <div className="app">
        <EmptyState
          icon="🔒"
          title="Откройте внутри Telegram"
          subtitle="Приложение авторизует вас по данным Telegram. Запустите его через кнопку мини-приложения у бота."
        />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1 className="header__title">Мои привычки</h1>
        <p className="header__subtitle">Отмечай каждый день и держи серию 🔥</p>
      </header>

      {error && (
        <div className="banner banner--error" onClick={() => setError(null)}>
          {error}
        </div>
      )}

      {loading ? (
        <Loader />
      ) : (
        <>
          {stats && habits.length > 0 && (
            <section className="panel">
              <StatsBar stats={stats} />
              <WeekChart stats={stats} />
            </section>
          )}

          {habits.length === 0 ? (
            <EmptyState
              icon="🌱"
              title="Пока нет привычек"
              subtitle="Добавьте первую привычку и начните серию уже сегодня."
              action={{
                label: 'Добавить привычку',
                onClick: () => {
                  draftRef.current = null;
                  setEditing({ mode: 'create' });
                },
              }}
            />
          ) : (
            <section className="list">
              {habits.map((h) => (
                <HabitCard
                  key={h.id}
                  habit={h}
                  busy={busyId === h.id}
                  onToggle={onToggle}
                  onEdit={(habit) => {
                    draftRef.current = {
                      title: habit.title,
                      emoji: habit.emoji,
                      color: habit.color,
                    };
                    setEditing({ mode: 'edit', habit });
                  }}
                />
              ))}
            </section>
          )}
        </>
      )}

      {editing && (
        <HabitForm
          initial={editing.mode === 'edit' ? editing.habit : null}
          submitting={submitting}
          onChange={(draft) => {
            draftRef.current = draft;
          }}
          onSubmit={(draft) => {
            draftRef.current = draft;
            void submitDraft();
          }}
          onDelete={editing.mode === 'edit' ? onDelete : undefined}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}
