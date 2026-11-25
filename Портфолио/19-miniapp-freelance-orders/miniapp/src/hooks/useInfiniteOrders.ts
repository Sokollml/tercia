import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchOrders } from '../api';
import type { Order, OrderFilters } from '../types';

const PAGE_SIZE = 20;

export interface InfiniteOrders {
  orders: Order[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => void;
  reload: () => void;
  patchOrder: (id: number, patch: Partial<Order>) => void;
}

/**
 * Лента заказов с бесконечной прокруткой. При смене filters — полный сброс.
 */
export function useInfiniteOrders(filters: OrderFilters): InfiniteOrders {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  const offsetRef = useRef(0);
  const loadingRef = useRef(false);
  // Токен запроса: гонки при быстрой смене фильтров не портят состояние.
  const reqRef = useRef(0);

  const load = useCallback(
    async (reset: boolean) => {
      if (loadingRef.current) return;
      loadingRef.current = true;
      setLoading(true);
      setError(null);

      const token = ++reqRef.current;
      const offset = reset ? 0 : offsetRef.current;

      try {
        const res = await fetchOrders(filters, PAGE_SIZE, offset);
        if (token !== reqRef.current) return; // устаревший ответ
        const items = res.items || [];
        setOrders((prev) => (reset ? items : [...prev, ...items]));
        offsetRef.current = offset + items.length;
        setHasMore(items.length >= PAGE_SIZE);
      } catch (e) {
        if (token !== reqRef.current) return;
        setError(e instanceof Error ? e.message : 'Ошибка загрузки');
        setHasMore(false);
      } finally {
        if (token === reqRef.current) setLoading(false);
        loadingRef.current = false;
      }
    },
    [filters],
  );

  // Сброс и первая загрузка при изменении фильтров.
  useEffect(() => {
    offsetRef.current = 0;
    setHasMore(true);
    void load(true);
  }, [load]);

  const loadMore = useCallback(() => {
    if (!loadingRef.current && hasMore) void load(false);
  }, [hasMore, load]);

  const reload = useCallback(() => {
    offsetRef.current = 0;
    setHasMore(true);
    void load(true);
  }, [load]);

  const patchOrder = useCallback((id: number, patch: Partial<Order>) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === id ? { ...o, ...patch } : o)),
    );
  }, []);

  return { orders, loading, error, hasMore, loadMore, reload, patchOrder };
}
