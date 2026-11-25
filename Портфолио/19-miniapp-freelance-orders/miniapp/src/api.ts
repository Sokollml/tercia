import WebApp from '@twa-dev/sdk';
import type {
  Order,
  OrderFilters,
  OrderUserStatus,
  UserSettings,
} from './types';
import { EMPTY_SETTINGS } from './types';

const BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');

// initData подписан ботом; бэкенд (n8n) валидирует HMAC. Шлём в заголовке.
function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': WebApp.initData || '',
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...authHeaders(), ...(init?.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

export interface OrdersResponse {
  items: Order[];
  limit: number;
  offset: number;
}

export async function fetchOrders(
  filters: OrderFilters,
  limit: number,
  offset: number,
): Promise<OrdersResponse> {
  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (filters.sort) params.set('sort', filters.sort);
  if (filters.service_type) params.set('service_type', filters.service_type);
  if (filters.urgency) params.set('urgency', filters.urgency);
  if (filters.min_budget != null) params.set('min_budget', String(filters.min_budget));
  if (filters.q) params.set('q', filters.q);
  if (filters.skills?.length) params.set('skills', filters.skills.join(','));
  if (filters.languages?.length) params.set('languages', filters.languages.join(','));

  return request<OrdersResponse>(`/orders?${params.toString()}`);
}

export async function getSettings(): Promise<UserSettings> {
  const data = await request<{ settings: Partial<UserSettings> }>('/settings');
  return { ...EMPTY_SETTINGS, ...(data.settings || {}) };
}

export async function saveSettings(settings: UserSettings): Promise<UserSettings> {
  const data = await request<{ ok: boolean; settings: Partial<UserSettings> }>(
    '/settings',
    { method: 'POST', body: JSON.stringify({ settings }) },
  );
  return { ...EMPTY_SETTINGS, ...(data.settings || {}) };
}

export async function setOrderStatus(
  orderId: number,
  status: OrderUserStatus,
  note: string | null,
): Promise<void> {
  await request('/order-status', {
    method: 'POST',
    body: JSON.stringify({ order_id: orderId, status, note }),
  });
}
