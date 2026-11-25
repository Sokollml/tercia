import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { getDb } from './db.js';
import { config } from './config.js';

/**
 * Простой раннер миграций. Читает .sql-файлы из backend/db/migrations в
 * алфавитном порядке и выполняет их. SQL написан для PostgreSQL; при работе на
 * SQLite (DB_DRIVER=sqlite, локально/тесты) выполняется лёгкая трансляция
 * диалекта — этого достаточно для нашей несложной схемы.
 *
 * Все стейтменты идемпотентны (CREATE TABLE/INDEX IF NOT EXISTS), поэтому
 * повторный запуск безопасен.
 */

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MIGRATIONS_DIR = path.resolve(__dirname, '../db/migrations');

/** Транслирует Postgres-DDL в диалект SQLite. */
function toSqlite(sql: string): string {
  return sql
    .replace(/BIGSERIAL\s+PRIMARY\s+KEY/gi, 'INTEGER PRIMARY KEY AUTOINCREMENT')
    .replace(/\bBIGSERIAL\b/gi, 'INTEGER')
    .replace(/\bBIGINT\b/gi, 'INTEGER')
    .replace(/\bTIMESTAMPTZ\b/gi, 'TEXT')
    .replace(/\bnow\(\)/gi, "CURRENT_TIMESTAMP");
}

/**
 * Разбивает файл на отдельные стейтменты по ';'. Сначала вырезаем строки-комментарии
 * (начинающиеся с --), иначе комментарий перед CREATE «прилипал» бы к стейтменту.
 * В нашей схеме ';' внутри строковых литералов нет, поэтому split безопасен.
 */
function splitStatements(sql: string): string[] {
  const withoutComments = sql.replace(/^\s*--.*$/gm, '');
  return withoutComments
    .split(';')
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

export async function migrate(): Promise<void> {
  const db = await getDb();
  const files = fs
    .readdirSync(MIGRATIONS_DIR)
    .filter((f) => f.endsWith('.sql'))
    .sort();

  for (const file of files) {
    const raw = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf8');
    const sql = config.dbDriver === 'sqlite' ? toSqlite(raw) : raw;
    for (const stmt of splitStatements(sql)) {
      await db.query(stmt);
    }
    // eslint-disable-next-line no-console
    console.log(`[migrate] применён ${file}`);
  }
}

// Запуск как CLI: `npm run migrate`.
const isCli = process.argv[1] && process.argv[1].endsWith('migrate.ts')
  || (process.argv[1] && process.argv[1].endsWith('migrate.js'));

if (isCli) {
  migrate()
    .then(async () => {
      const db = await getDb();
      await db.close();
      // eslint-disable-next-line no-console
      console.log('[migrate] готово');
      process.exit(0);
    })
    .catch((err) => {
      // eslint-disable-next-line no-console
      console.error('[migrate] ошибка:', err);
      process.exit(1);
    });
}
