/**
 * Storage abstraction.
 *
 * The rest of the app talks to a `Store`, never to `pg` directly. This keeps
 * the HTTP/business layers persistence-agnostic and — crucially — lets the
 * tests run against a fast in-memory implementation without a live Postgres.
 *
 * Two implementations exist:
 *   - PgStore     (src/pg-store.ts)     — production, PostgreSQL.
 *   - MemoryStore (src/memory-store.ts) — tests & local prototyping.
 */

export interface UserRow {
  id: number;
  tgId: number;
  username: string | null;
  firstName: string | null;
  lastName: string | null;
  isAdmin: boolean;
}

export interface CardRow {
  id: number;
  userId: number;
  code: string;
  stamps: number;
  rewardsEarned: number;
  rewardsRedeemed: number;
}

export interface UpsertUserInput {
  tgId: number;
  username?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  isAdmin: boolean;
}

export interface GrantStampResult {
  /** Card state after the operation. */
  card: CardRow;
  /** True when this stamp completed a card and produced a reward. */
  rewardGranted: boolean;
  /** Stamps still needed for the next reward. */
  remaining: number;
  /**
   * True when the idempotency key had already been used — i.e. this was a
   * duplicate/replayed request (double scan) and NOTHING was changed.
   */
  alreadyApplied: boolean;
}

export interface Stats {
  totalCustomers: number;
  activeCards: number;
  totalStamps: number;
  rewardsEarned: number;
  stampsToday: number;
}

export interface Store {
  upsertUser(input: UpsertUserInput): Promise<UserRow>;
  getUserByTgId(tgId: number): Promise<UserRow | null>;
  getUserById(id: number): Promise<UserRow | null>;
  getOrCreateCard(userId: number): Promise<CardRow>;
  getCardByUserId(userId: number): Promise<CardRow | null>;
  getCardByCode(code: string): Promise<CardRow | null>;
  /**
   * Grant one stamp to a card. Implementations MUST be atomic and MUST honour
   * `idempotencyKey`: a repeated key never grants a second stamp.
   */
  grantStamp(
    cardId: number,
    adminUserId: number,
    idempotencyKey: string,
    threshold: number,
  ): Promise<GrantStampResult>;
  stats(): Promise<Stats>;
  /** Release any underlying resources (connection pool). */
  close(): Promise<void>;
}
