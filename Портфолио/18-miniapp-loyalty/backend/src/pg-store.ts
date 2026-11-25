import { pool, withTransaction } from './db.js';
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

/** Column shapes as they come back from Postgres (snake_case). */
interface DbUser {
  id: string;
  tg_id: string;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  is_admin: boolean;
}
interface DbCard {
  id: string;
  user_id: string;
  code: string;
  stamps: number;
  rewards_earned: number;
  rewards_redeemed: number;
}

function mapUser(r: DbUser): UserRow {
  return {
    id: Number(r.id),
    tgId: Number(r.tg_id),
    username: r.username,
    firstName: r.first_name,
    lastName: r.last_name,
    isAdmin: r.is_admin,
  };
}
function mapCard(r: DbCard): CardRow {
  return {
    id: Number(r.id),
    userId: Number(r.user_id),
    code: r.code,
    stamps: r.stamps,
    rewardsEarned: r.rewards_earned,
    rewardsRedeemed: r.rewards_redeemed,
  };
}

/** PostgreSQL-backed Store. */
export class PgStore implements Store {
  async upsertUser(input: UpsertUserInput): Promise<UserRow> {
    // Insert-or-update on the unique tg_id. `is_admin` is always driven by the
    // server's ADMIN_IDS config, never by anything the client sends.
    const { rows } = await pool.query<DbUser>(
      `INSERT INTO users (tg_id, username, first_name, last_name, is_admin)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (tg_id) DO UPDATE SET
         username   = EXCLUDED.username,
         first_name = EXCLUDED.first_name,
         last_name  = EXCLUDED.last_name,
         is_admin   = EXCLUDED.is_admin,
         updated_at = now()
       RETURNING *`,
      [
        input.tgId,
        input.username ?? null,
        input.firstName ?? null,
        input.lastName ?? null,
        input.isAdmin,
      ],
    );
    return mapUser(rows[0]);
  }

  async getUserByTgId(tgId: number): Promise<UserRow | null> {
    const { rows } = await pool.query<DbUser>(
      `SELECT * FROM users WHERE tg_id = $1`,
      [tgId],
    );
    return rows[0] ? mapUser(rows[0]) : null;
  }

  async getUserById(id: number): Promise<UserRow | null> {
    const { rows } = await pool.query<DbUser>(
      `SELECT * FROM users WHERE id = $1`,
      [id],
    );
    return rows[0] ? mapUser(rows[0]) : null;
  }

  async getOrCreateCard(userId: number): Promise<CardRow> {
    const existing = await this.getCardByUserId(userId);
    if (existing) return existing;

    // Retry a few times on the (astronomically unlikely) code collision.
    for (let attempt = 0; attempt < 5; attempt++) {
      const code = generateCardCode();
      try {
        const { rows } = await pool.query<DbCard>(
          `INSERT INTO cards (user_id, code) VALUES ($1, $2) RETURNING *`,
          [userId, code],
        );
        return mapCard(rows[0]);
      } catch (err: unknown) {
        // 23505 = unique_violation. If the *user* already has a card (race),
        // fetch it; otherwise it was a code clash — try a new code.
        if (isUniqueViolation(err)) {
          const again = await this.getCardByUserId(userId);
          if (again) return again;
          continue;
        }
        throw err;
      }
    }
    throw new Error('failed_to_create_card');
  }

  async getCardByUserId(userId: number): Promise<CardRow | null> {
    const { rows } = await pool.query<DbCard>(
      `SELECT * FROM cards WHERE user_id = $1`,
      [userId],
    );
    return rows[0] ? mapCard(rows[0]) : null;
  }

  async getCardByCode(code: string): Promise<CardRow | null> {
    const { rows } = await pool.query<DbCard>(
      `SELECT * FROM cards WHERE code = $1`,
      [code],
    );
    return rows[0] ? mapCard(rows[0]) : null;
  }

  async grantStamp(
    cardId: number,
    adminUserId: number,
    idempotencyKey: string,
    threshold: number,
  ): Promise<GrantStampResult> {
    return withTransaction(async (client) => {
      // 1. Idempotency guard. If we've already seen this key, this is a
      //    duplicate scan — return the current state untouched.
      const dup = await client.query<{ completed_card: boolean }>(
        `SELECT completed_card FROM stamps WHERE idempotency_key = $1`,
        [idempotencyKey],
      );
      if (dup.rows[0]) {
        const cur = await client.query<DbCard>(
          `SELECT * FROM cards WHERE id = $1`,
          [cardId],
        );
        const card = mapCard(cur.rows[0]);
        return {
          card,
          rewardGranted: dup.rows[0].completed_card,
          remaining: stampsRemaining(
            { stamps: card.stamps, rewardsEarned: card.rewardsEarned },
            threshold,
          ),
          alreadyApplied: true,
        };
      }

      // 2. Lock the card row so concurrent scans serialize.
      const locked = await client.query<DbCard>(
        `SELECT * FROM cards WHERE id = $1 FOR UPDATE`,
        [cardId],
      );
      if (!locked.rows[0]) throw new Error('card_not_found');
      const before = mapCard(locked.rows[0]);

      // 3. Pure business rule decides the next state.
      const outcome = applyStamp(
        { stamps: before.stamps, rewardsEarned: before.rewardsEarned },
        threshold,
      );

      // 4. Persist new card state + append to the immutable ledger.
      const updated = await client.query<DbCard>(
        `UPDATE cards
           SET stamps = $1, rewards_earned = $2, updated_at = now()
         WHERE id = $3
         RETURNING *`,
        [outcome.next.stamps, outcome.next.rewardsEarned, cardId],
      );
      await client.query(
        `INSERT INTO stamps (card_id, granted_by, idempotency_key, completed_card)
         VALUES ($1, $2, $3, $4)`,
        [cardId, adminUserId, idempotencyKey, outcome.rewardGranted],
      );

      return {
        card: mapCard(updated.rows[0]),
        rewardGranted: outcome.rewardGranted,
        remaining: outcome.remaining,
        alreadyApplied: false,
      };
    });
  }

  async stats(): Promise<Stats> {
    const { rows } = await pool.query<{
      total_customers: string;
      active_cards: string;
      total_stamps: string;
      rewards_earned: string;
      stamps_today: string;
    }>(
      `SELECT
         (SELECT count(*) FROM users)                                  AS total_customers,
         (SELECT count(*) FROM cards WHERE stamps > 0)                 AS active_cards,
         (SELECT count(*) FROM stamps)                                 AS total_stamps,
         (SELECT COALESCE(sum(rewards_earned), 0) FROM cards)          AS rewards_earned,
         (SELECT count(*) FROM stamps WHERE created_at >= date_trunc('day', now())) AS stamps_today`,
    );
    const r = rows[0];
    return {
      totalCustomers: Number(r.total_customers),
      activeCards: Number(r.active_cards),
      totalStamps: Number(r.total_stamps),
      rewardsEarned: Number(r.rewards_earned),
      stampsToday: Number(r.stamps_today),
    };
  }

  async close(): Promise<void> {
    await pool.end();
  }
}

function isUniqueViolation(err: unknown): boolean {
  return (
    typeof err === 'object' &&
    err !== null &&
    'code' in err &&
    (err as { code?: string }).code === '23505'
  );
}
