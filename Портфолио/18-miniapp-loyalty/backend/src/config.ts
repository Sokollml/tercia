import 'dotenv/config';

/**
 * Centralised, validated configuration.
 * Everything that can be tuned lives here so the rest of the code never
 * reaches into process.env directly.
 */

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function optional(name: string, fallback: string): string {
  return process.env[name] ?? fallback;
}

/** Parse comma / space separated list of numeric Telegram ids. */
export function parseAdminIds(raw: string | undefined): Set<number> {
  const ids = new Set<number>();
  if (!raw) return ids;
  for (const part of raw.split(/[,\s]+/)) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    const n = Number(trimmed);
    if (Number.isFinite(n)) ids.add(n);
  }
  return ids;
}

export const config = {
  botToken: required('BOT_TOKEN'),
  port: Number(optional('PORT', '3000')),
  host: optional('HOST', '0.0.0.0'),

  // Admins (cafe staff) are identified purely by their Telegram id.
  adminIds: parseAdminIds(process.env.ADMIN_IDS),

  // How many stamps a customer must collect before a reward is granted.
  stampsPerReward: Number(optional('STAMPS_PER_REWARD', '8')),

  // initData older than this (seconds) is rejected as a replay attempt.
  initDataMaxAgeSeconds: Number(optional('INITDATA_MAX_AGE_SECONDS', '86400')),

  // CORS origin of the deployed mini-app (Vercel URL).
  miniappUrl: optional('MINIAPP_URL', '*'),

  database: {
    host: optional('DB_HOST', 'localhost'),
    port: Number(optional('DB_PORT', '5432')),
    user: optional('DB_USER', 'loyalty'),
    password: optional('DB_PASSWORD', 'loyalty'),
    name: optional('DB_NAME', 'loyalty'),
    // Full URL takes precedence when provided (Railway / Heroku style).
    url: process.env.DATABASE_URL,
    ssl: process.env.DB_SSL === 'true',
  },
} as const;

export type AppConfig = typeof config;
