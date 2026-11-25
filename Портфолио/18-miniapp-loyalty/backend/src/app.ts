import Fastify, { type FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import { makeAuthPreHandler, requireUser } from './auth.js';
import {
  BadRequestError,
  ForbiddenError,
  NotFoundError,
  getMyCard,
  grantStampByCode,
  lookupCard,
} from './service.js';
import type { Store } from './store.js';

export interface AppOptions {
  store: Store;
  botToken: string;
  adminIds: Set<number>;
  stampsPerReward: number;
  initDataMaxAgeSeconds: number;
  corsOrigin: string;
}

/**
 * Build the Fastify application. Everything it needs is injected, so tests can
 * construct an app around a MemoryStore and a throwaway bot token.
 */
export function buildApp(opts: AppOptions): FastifyInstance {
  const app = Fastify({ logger: false });

  app.register(cors, {
    origin: opts.corsOrigin === '*' ? true : opts.corsOrigin,
    methods: ['GET', 'POST'],
    allowedHeaders: ['content-type', 'x-telegram-init-data'],
  });

  // Health check — the only unauthenticated route.
  app.get('/health', async () => ({ ok: true }));

  const auth = makeAuthPreHandler({
    store: opts.store,
    botToken: opts.botToken,
    adminIds: opts.adminIds,
    maxAgeSeconds: opts.initDataMaxAgeSeconds,
  });

  // Everything under /api requires a valid, signed initData.
  app.register(
    async (api) => {
      api.addHook('preHandler', auth);

      // --- Identity + own card (customer or admin) ---------------------
      api.get('/me', async (request) => {
        const user = requireUser(request);
        const card = await getMyCard(opts.store, user, opts.stampsPerReward);
        return {
          role: user.isAdmin ? 'admin' : 'customer',
          user: {
            id: user.tgId,
            firstName: user.firstName,
            username: user.username,
          },
          card,
        };
      });

      // --- Admin: grant a stamp by code (from QR scan or manual entry) --
      api.post('/admin/stamp', async (request) => {
        const admin = requireUser(request);
        const body = (request.body ?? {}) as {
          code?: string;
          idempotencyKey?: string;
        };
        return grantStampByCode(
          opts.store,
          admin,
          {
            code: body.code ?? '',
            idempotencyKey: body.idempotencyKey ?? '',
          },
          opts.stampsPerReward,
        );
      });

      // --- Admin: preview a card before stamping -----------------------
      api.get('/admin/lookup', async (request) => {
        const admin = requireUser(request);
        const { code } = (request.query ?? {}) as { code?: string };
        return lookupCard(opts.store, admin, code ?? '', opts.stampsPerReward);
      });

      // --- Admin: cafe statistics --------------------------------------
      api.get('/admin/stats', async (request) => {
        const admin = requireUser(request);
        if (!admin.isAdmin) {
          throw new ForbiddenError('admin_only');
        }
        return opts.store.stats();
      });
    },
    { prefix: '/api' },
  );

  // Map domain errors to HTTP status codes.
  app.setErrorHandler((error, _request, reply) => {
    if (error instanceof ForbiddenError) {
      return reply.code(403).send({ error: error.message });
    }
    if (error instanceof NotFoundError) {
      return reply.code(404).send({ error: error.message });
    }
    if (error instanceof BadRequestError) {
      return reply.code(400).send({ error: error.message });
    }
    return reply.code(500).send({ error: 'internal_error' });
  });

  return app;
}
