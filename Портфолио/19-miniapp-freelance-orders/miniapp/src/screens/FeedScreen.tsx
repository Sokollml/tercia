import { useEffect, useMemo, useRef, useState } from 'react';
import { SortBar } from '../components/SortBar';
import { OrderCard } from '../components/OrderCard';
import { useInfiniteOrders } from '../hooks/useInfiniteOrders';
import type { Order, OrderFilters, SortKey, UserSettings } from '../types';

interface FeedScreenProps {
  settings: UserSettings;
  onOpenOrder: (order: Order) => void;
  registerReload: (fn: () => void) => void;
}

export function FeedScreen({ settings, onOpenOrder, registerReload }: FeedScreenProps) {
  const [sort, setSort] = useState<SortKey>('new');
  const [onlyMatched, setOnlyMatched] = useState(false);

  const filters = useMemo<OrderFilters>(() => {
    const base: OrderFilters = { sort };
    if (onlyMatched) {
      if (settings.skills.length) base.skills = settings.skills;
      if (settings.languages.length) base.languages = settings.languages;
      if (settings.min_budget != null) base.min_budget = settings.min_budget;
    }
    return base;
  }, [sort, onlyMatched, settings]);

  const { orders, loading, error, hasMore, loadMore, reload } =
    useInfiniteOrders(filters);

  // Даём родителю возможность перезагрузить ленту (после смены статуса заказа).
  useEffect(() => {
    registerReload(reload);
  }, [registerReload, reload]);

  // Бесконечная прокрутка через IntersectionObserver.
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) loadMore();
      },
      { rootMargin: '200px' },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [loadMore]);

  return (
    <div className="screen">
      <SortBar
        value={sort}
        onChange={setSort}
        onlyMatched={onlyMatched}
        onToggleMatched={setOnlyMatched}
      />

      {error && <div className="notice notice--error">{error}</div>}

      {!loading && !error && orders.length === 0 && (
        <div className="empty">
          <div className="empty__emoji">🗂️</div>
          <p>Пока нет заказов по этим фильтрам.</p>
        </div>
      )}

      <div className="feed">
        {orders.map((o) => (
          <OrderCard key={o.id} order={o} onOpen={onOpenOrder} />
        ))}
      </div>

      {loading && <div className="loader">Загрузка…</div>}
      {hasMore && <div ref={sentinelRef} className="sentinel" />}
    </div>
  );
}
