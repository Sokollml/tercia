import { getInitData } from './telegram.js';
import type {
  GrantStampResponse,
  MeResponse,
  StatsResponse,
} from './types.js';

/**
 * Backend API client.
 *
 * Every request carries the Telegram `initData` in the `x-telegram-init-data`
 * header; the backend verifies its signature and derives the user's identity
 * and role from it. We never send the user id ourselves — it can't be trusted.
 */

const BASE_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
  ) {
    super(code);
    this.name = 'ApiError';
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      'x-telegram-init-data': getInitData(),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    let code = `http_${res.status}`;
    try {
      const body = (await res.json()) as { error?: string; reason?: string };
      code = body.error ?? body.reason ?? code;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, code);
  }
  return (await res.json()) as T;
}

export function getMe(): Promise<MeResponse> {
  return request<MeResponse>('/api/me');
}

export function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>('/api/admin/stats');
}

export function grantStamp(
  code: string,
  idempotencyKey: string,
): Promise<GrantStampResponse> {
  return request<GrantStampResponse>('/api/admin/stamp', {
    method: 'POST',
    body: JSON.stringify({ code, idempotencyKey }),
  });
}
