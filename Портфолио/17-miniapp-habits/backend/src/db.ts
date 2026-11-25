import { config } from './config.js';

/**
 * Тонкий слой абстракции над БД, чтобы код роутов не зависел от драйвера.
 *
 * Целевая БД — PostgreSQL (драйвер `pg`). Для локальной разработки и тестов
 * можно переключиться на SQLite (`better-sqlite3`) флагом DB_DRIVER=sqlite.
 *
 * Единый интерфейс: query(sql, params) -> { rows }.
 * SQL пишем в стиле Postgres с плейсхолдерами $1, $2, ...; для SQLite они
 * автоматически конвертируются в позиционные `?`.
 */
export interface QueryResult<T = any> {
  rows: T[];
}

export interface Db {
  query<T = any>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
  close(): Promise<void>;
}

// ── PostgreSQL ──────────────────────────────────────────────────────────────
async function createPostgres(): Promise<Db> {
  const { default: pg } = await import('pg');
  const pool = config.databaseUrl
    ? new pg.Pool({ connectionString: config.databaseUrl })
    : new pg.Pool({
        host: config.pg.host,
        port: config.pg.port,
        user: config.pg.user,
        password: config.pg.password,
        database: config.pg.database,
      });

  return {
    async query<T>(sql: string, params: unknown[] = []) {
      const res = await pool.query(sql, params as any[]);
      return { rows: res.rows as T[] };
    },
    async close() {
      await pool.end();
    },
  };
}

// ── SQLite ────────────────────────────────────────────────────────────────
async function createSqlite(): Promise<Db> {
  const { default: Database } = await import('better-sqlite3');
  const db = new Database(config.sqlitePath);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');

  // Postgres-плейсхолдеры $1,$2 → позиционные `?` (по порядку появления).
  const toSqlite = (sql: string) => sql.replace(/\$\d+/g, '?');

  return {
    async query<T>(sql: string, params: unknown[] = []) {
      const stmt = db.prepare(toSqlite(sql));
      // Если запрос возвращает строки (SELECT / ... RETURNING) — .all(),
      // иначе — .run(). better-sqlite3 помечает такие стейтменты .reader.
      if ((stmt as any).reader) {
        const rows = stmt.all(...(params as any[])) as T[];
        return { rows };
      }
      stmt.run(...(params as any[]));
      return { rows: [] as T[] };
    },
    async close() {
      db.close();
    },
  };
}

let instance: Db | null = null;

export async function getDb(): Promise<Db> {
  if (instance) return instance;
  instance = config.dbDriver === 'sqlite' ? await createSqlite() : await createPostgres();
  return instance;
}
