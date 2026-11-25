import { applyStamp, stampsRemaining } from './lib/loyalty.js';
import { generateCardCode } from './lib/code.js';
import type {
  CardRow,
  GrantStampResult,
  Stats,
  Store,
  UpsertUserInput,
  UserRow,
} from './store.js';

/**
 * In-memory Store implementation.
 *
 * Used by the test-suite (so the loyalty rules and authorization can be
 * verified without a database) and handy for local prototyping. It mirrors the
 * exact semantics of PgStore, including anti-double-scan via idempotency keys.
 */
export class MemoryStore implements Store {
  private users = new Map<number, UserRow>(); // key: user.id
  private usersByTg = new Map<number, number>(); // tgId -> user.id
  private cards = new Map<number, CardRow>(); // key: card.id
  private cardsByUser = new Map<number, number>(); // userId -> card.id
  private cardsByCode = new Map<string, number>(); // code -> card.id
  private usedKeys = new Map<string, boolean>(); // idempotencyKey -> completed_card
  private stampCount = 0;
  private stampsTodayCount = 0;
  private nextUserId = 1;
  private nextCardId = 1;

  async upsertUser(input: UpsertUserInput): Promise<UserRow> {
    const existingId = this.usersByTg.get(input.tgId);
    if (existingId != null) {
      const existing = this.users.get(existingId)!;
      const updated: UserRow = {
        ...existing,
        username: input.username ?? null,
        firstName: input.firstName ?? null,
        lastName: input.lastName ?? null,
        isAdmin: input.isAdmin,
      };
      this.users.set(existingId, updated);
      return updated;
    }
    const user: UserRow = {
      id: this.nextUserId++,
      tgId: input.tgId,
      username: input.username ?? null,
      firstName: input.firstName ?? null,
      lastName: input.lastName ?? null,
      isAdmin: input.isAdmin,
    };
    this.users.set(user.id, user);
    this.usersByTg.set(user.tgId, user.id);
    return user;
  }

  async getUserByTgId(tgId: number): Promise<UserRow | null> {
    const id = this.usersByTg.get(tgId);
    return id != null ? this.users.get(id) ?? null : null;
  }

  async getUserById(id: number): Promise<UserRow | null> {
    return this.users.get(id) ?? null;
  }

  async getOrCreateCard(userId: number): Promise<CardRow> {
    const existing = this.cardsByUser.get(userId);
    if (existing != null) return this.cards.get(existing)!;
    let code = generateCardCode();
    while (this.cardsByCode.has(code)) code = generateCardCode();
    const card: CardRow = {
      id: this.nextCardId++,
      userId,
      code,
      stamps: 0,
      rewardsEarned: 0,
      rewardsRedeemed: 0,
    };
    this.cards.set(card.id, card);
    this.cardsByUser.set(userId, card.id);
    this.cardsByCode.set(code, card.id);
    return card;
  }

  async getCardByUserId(userId: number): Promise<CardRow | null> {
    const id = this.cardsByUser.get(userId);
    return id != null ? this.cards.get(id) ?? null : null;
  }

  async getCardByCode(code: string): Promise<CardRow | null> {
    const id = this.cardsByCode.get(code);
    return id != null ? this.cards.get(id) ?? null : null;
  }

  async grantStamp(
    cardId: number,
    _adminUserId: number,
    idempotencyKey: string,
    threshold: number,
  ): Promise<GrantStampResult> {
    const card = this.cards.get(cardId);
    if (!card) throw new Error('card_not_found');

    // Anti double-scan: a re-used key changes nothing.
    if (this.usedKeys.has(idempotencyKey)) {
      const rewardGranted = this.usedKeys.get(idempotencyKey)!;
      return {
        card: { ...card },
        rewardGranted,
        remaining: stampsRemaining(
          { stamps: card.stamps, rewardsEarned: card.rewardsEarned },
          threshold,
        ),
        alreadyApplied: true,
      };
    }

    const outcome = applyStamp(
      { stamps: card.stamps, rewardsEarned: card.rewardsEarned },
      threshold,
    );
    card.stamps = outcome.next.stamps;
    card.rewardsEarned = outcome.next.rewardsEarned;

    this.usedKeys.set(idempotencyKey, outcome.rewardGranted);
    this.stampCount++;
    this.stampsTodayCount++;

    return {
      card: { ...card },
      rewardGranted: outcome.rewardGranted,
      remaining: outcome.remaining,
      alreadyApplied: false,
    };
  }

  async stats(): Promise<Stats> {
    let activeCards = 0;
    let rewardsEarned = 0;
    for (const card of this.cards.values()) {
      if (card.stamps > 0) activeCards++;
      rewardsEarned += card.rewardsEarned;
    }
    return {
      totalCustomers: this.users.size,
      activeCards,
      totalStamps: this.stampCount,
      rewardsEarned,
      stampsToday: this.stampsTodayCount,
    };
  }

  async close(): Promise<void> {
    /* nothing to release */
  }
}
