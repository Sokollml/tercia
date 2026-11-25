import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { pool } from './db.js';

/**
 * Tiny migration runner: applies db/schema.sql. Idempotent thanks to the
 * `CREATE TABLE IF NOT EXISTS` statements. Run with `npm run migrate`.
 */
const __dirname = dirname(fileURLToPath(import.meta.url));

async function main() {
  const schemaPath = join(__dirname, '..', 'db', 'schema.sql');
  const sql = await readFile(schemaPath, 'utf8');
  await pool.query(sql);
  // eslint-disable-next-line no-console
  console.log('✓ Schema applied');
  await pool.end();
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('Migration failed:', err);
  process.exit(1);
});
