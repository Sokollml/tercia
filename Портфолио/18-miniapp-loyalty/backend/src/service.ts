import { normalizeCode } from './lib/code.js';
import { stampsRemaining } from './lib/loyalty.js';
import type { CardRow, Store, UserRow } from './store.js';

/**
 * Application service layer: the business operations the HTTP routes expose,
 * plus the authorization rules that guard them. Deliberately free of Fastify
 * so it can be unit-tested directly against a MemoryStore.
 */

export class ForbiddenError extends Error {
  constructor(message = 'forbidden') {
    super(message);
    this.name = 'ForbiddenError';
  }
}
export class NotFoundError extends Error {
  constructor(message = 'not_found') {
    super(message);
    this.name = 'NotFoundError';
  }
}
export class BadRequestError extends Error {
  constructor(message = 'bad_request') {
    super(message);
    this.name = 'BadRequestError';
  }
}

/** Public, client-safe view of a loyalty card. */
export interface CardView {
  code: string;
  stamps: number;
  threshold: number;
  remaining: number;
  rewardsEarned: number;
  rewardsRedeemed: number;
}

export function toCardView(card: CardRow, threshold: number): CardView {
  return {
    code: card.code,
    stamps: card.stamps,
    threshold,
    remaining: stampsRemaining(
      { stamps: card.stamps, rewardsEarned: card.rewardsEarned },
      threshold,
    ),
    rewardsEarned: card.rewardsEarned,
    rewardsRedeemed: card.rewardsRedeemed,
  };
}

/** The current user's own card (created lazily on first access). */
export async function getMyCard(
  store: Store,
  user: UserRow,
  threshold: number,
): Promise<CardView> {
  const card = await store.getOrCreateCard(user.id);
  return toCardView(card, threshold);
}

export interface GrantStampInput {
  code: string;
  idempotencyKey: string;
}

export interface GrantStampView {
  card: CardView;
  rewardGranted: boolean;
  alreadyApplied: boolean;
  customer: {
    firstName: string | null;
    username: string | null;
  };
}

/**
 * Grant a stamp to the card identified by `code`.
 *
 * Authorization: ONLY an admin (cafe staff, identified by Telegram id in
 * ADMIN_IDS) may do this. A non-admin caller is rejected before any DB write.
 */
export async function grantStampByCode(
  store: Store,
  admin: UserRow,
  input: GrantStampInput,
  threshold: number,
): Promise<GrantStampView> {
  if (!admin.isAdmin) {
    throw new ForbiddenError('admin_only');
  }
  const code = normalizeCode(input.code ?? '');
  if (!code) throw new BadRequestError('empty_code');
  if (!input.idempotencyKey || typeof input.idempotencyKey !== 'string') {
    throw new BadRequestError('missing_idempotency_key');
  }

  const card = await store.getCardByCode(code);
  if (!card) throw new NotFoundError('card_not_found');

  const result = await store.grantStamp(
    card.id,
    admin.id,
    input.idempotencyKey,
    threshold,
  );

  const owner = await findCardOwner(store, result.card);
  return {
    card: toCardView(result.card, threshold),
    rewardGranted: result.rewardGranted,
    alreadyApplied: result.alreadyApplied,
    customer: {
      firstName: owner?.firstName ?? null,
      username: owner?.username ?? null,
    },
  };
}

/** Look up a card by code (admin-only), for a pre-scan preview. */
export async function lookupCard(
  store: Store,
  admin: UserRow,
  code: string,
  threshold: number,
): Promise<CardView & { customer: { firstName: string | null; username: string | null } }> {
  if (!admin.isAdmin) throw new ForbiddenError('admin_only');
  const normalized = normalizeCode(code ?? '');
  if (!normalized) throw new BadRequestError('empty_code');
  const card = await store.getCardByCode(normalized);
  if (!card) throw new NotFoundError('card_not_found');
  const owner = await findCardOwner(store, card);
  return {
    ...toCardView(card, threshold),
    customer: {
      firstName: owner?.firstName ?? null,
      username: owner?.username ?? null,
    },
  };
}

async function findCardOwner(store: Store, card: CardRow): Promise<UserRow | null> {
  return store.getUserById(card.userId);
}
