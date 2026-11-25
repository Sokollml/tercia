import { buildApp } from './app.js';
import { config } from './config.js';
import { PgStore } from './pg-store.js';

/**
 * Production entrypoint: wire a real Postgres-backed store into the app and
 * start listening. Configuration comes entirely from environment variables
 * (see .env.example and src/config.ts).
 */
async function main() {
  const store = new PgStore();
  const app = buildApp({
    store,
    botToken: config.botToken,
    adminIds: config.adminIds,
    stampsPerReward: config.stampsPerReward,
    initDataMaxAgeSeconds: config.initDataMaxAgeSeconds,
    corsOrigin: config.miniappUrl,
  });

  const shutdown = async () => {
    await app.close();
    await store.close();
    process.exit(0);
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  await app.listen({ port: config.port, host: config.host });
  // eslint-disable-next-line no-console
  console.log(
    `Loyalty API listening on http://${config.host}:${config.port} ` +
      `(reward every ${config.stampsPerReward} stamps, ${config.adminIds.size} admin(s))`,
  );
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('Fatal startup error:', err);
  process.exit(1);
});
