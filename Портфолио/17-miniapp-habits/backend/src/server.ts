import { config, assertConfig } from './config.js';
import { getDb } from './db.js';
import { buildApp } from './app.js';
import { migrate } from './migrate.js';

/**
 * Точка входа сервера: проверяем конфиг, применяем миграции, поднимаем Fastify.
 */
async function main() {
  assertConfig();

  const db = await getDb();
  await migrate(); // идемпотентно — безопасно при каждом старте

  const app = buildApp(db);

  try {
    await app.listen({ port: config.port, host: '0.0.0.0' });
    // eslint-disable-next-line no-console
    console.log(`[server] слушаю на :${config.port} (БД: ${config.dbDriver})`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }

  // Аккуратное завершение.
  const shutdown = async () => {
    await app.close();
    await db.close();
    process.exit(0);
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('[server] фатальная ошибка запуска:', err);
  process.exit(1);
});
