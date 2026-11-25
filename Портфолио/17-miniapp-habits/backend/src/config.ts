import 'dotenv/config';

/**
 * Централизованная конфигурация из переменных окружения.
 * Все значения читаются один раз при старте.
 */
export interface Config {
  port: number;
  botToken: string;
  miniappUrls: string[];
  dbDriver: 'postgres' | 'sqlite';
  databaseUrl?: string;
  pg: {
    host: string;
    port: number;
    user: string;
    password: string;
    database: string;
  };
  sqlitePath: string;
  initDataMaxAgeSec: number;
}

function env(name: string, fallback = ''): string {
  const v = process.env[name];
  return v === undefined || v === '' ? fallback : v;
}

export const config: Config = {
  port: Number(env('PORT', '8080')),
  botToken: env('BOT_TOKEN'),
  miniappUrls: env('MINIAPP_URL', 'http://localhost:5173')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  dbDriver: (env('DB_DRIVER', 'postgres') as Config['dbDriver']),
  databaseUrl: env('DATABASE_URL') || undefined,
  pg: {
    host: env('DB_HOST', 'localhost'),
    port: Number(env('DB_PORT', '5432')),
    user: env('DB_USER', 'habits'),
    password: env('DB_PASSWORD', 'habits'),
    database: env('DB_NAME', 'habits'),
  },
  sqlitePath: env('SQLITE_PATH', './habits.sqlite'),
  initDataMaxAgeSec: Number(env('INITDATA_MAX_AGE_SEC', '86400')),
};

export function assertConfig(): void {
  if (!config.botToken) {
    throw new Error(
      'BOT_TOKEN не задан. Скопируйте .env.example в .env и укажите токен из @BotFather.'
    );
  }
}
