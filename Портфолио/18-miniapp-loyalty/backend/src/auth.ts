import type { FastifyReply, FastifyRequest } from 'fastify';
import { validateInitData } from './lib/telegram.js';
import type { Store, UserRow } from './store.js';

/**
 * Authentication for every /api request.
 *
 * The mini-app sends Telegram's signed `initData` in the `x-telegram-init-data`
 * header on every call. We:
 *   1. Verify the HMAC signature against our bot token (see lib/telegram.ts).
 *   2. Decide the role: a user is an admin iff their Telegram id is in
 *      ADMIN_IDS — this comes from server config, never from the client.
 *   3. Upsert the user and attach the resulting row to the request.
 *
 * Any request that fails validation is rejected with 401 before it can touch
 * business logic, so an attacker cannot forge an "admin" identity.
 */

export interface AuthDeps {
  store: Store;
  botToken: string;
  adminIds: Set<number>;
  maxAgeSeconds: number;
}

// Augment FastifyRequest with the authenticated user.
declare module 'fastify' {
  interface FastifyRequest {
    authUser?: UserRow;
  }
}

const INIT_DATA_HEADER = 'x-telegram-init-data';

export function makeAuthPreHandler(deps: AuthDeps) {
  return async function authPreHandler(
    request: FastifyRequest,
    reply: FastifyReply,
  ): Promise<void> {
    const header = request.headers[INIT_DATA_HEADER];
    const initData = Array.isArray(header) ? header[0] : header;

    const result = validateInitData(
      initData ?? '',
      deps.botToken,
      deps.maxAgeSeconds,
    );
    if (!result.ok) {
      reply.code(401).send({ error: 'unauthorized', reason: result.reason });
      return;
    }

    const isAdmin = deps.adminIds.has(result.user.id);
    const user = await deps.store.upsertUser({
      tgId: result.user.id,
      username: result.user.username ?? null,
      firstName: result.user.first_name ?? null,
      lastName: result.user.last_name ?? null,
      isAdmin,
    });

    request.authUser = user;
  };
}

/** Retrieve the authenticated user or throw (routes run after the preHandler). */
export function requireUser(request: FastifyRequest): UserRow {
  if (!request.authUser) {
    // Should be unreachable: the preHandler always sets it or 401s.
    throw new Error('auth_user_missing');
  }
  return request.authUser;
}
