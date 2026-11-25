import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryStore } from '../src/memory-store.js';
import {
  ForbiddenError,
  NotFoundError,
  getMyCard,
  grantStampByCode,
} from '../src/service.js';
import type { UserRow } from '../src/store.js';

const THRESHOLD = 8;

async function seedCustomer(store: MemoryStore): Promise<{ user: UserRow; code: string }> {
  const user = await store.upsertUser({
    tgId: 1001,
    firstName: 'Cust',
    username: 'cust',
    isAdmin: false,
  });
  const view = await getMyCard(store, user, THRESHOLD);
  return { user, code: view.code };
}

async function seedAdmin(store: MemoryStore): Promise<UserRow> {
  return store.upsertUser({
    tgId: 500,
    firstName: 'Barista',
    isAdmin: true,
  });
}

describe('grantStampByCode', () => {
  let store: MemoryStore;
  beforeEach(() => {
    store = new MemoryStore();
  });

  it('grants a reward and resets the card on the Nth stamp', async () => {
    const admin = await seedAdmin(store);
    const { code } = await seedCustomer(store);

    let last;
    for (let i = 1; i <= THRESHOLD; i++) {
      last = await grantStampByCode(
        store,
        admin,
        { code, idempotencyKey: `key-${i}` },
        THRESHOLD,
      );
      if (i < THRESHOLD) {
        expect(last.rewardGranted).toBe(false);
        expect(last.card.stamps).toBe(i);
        expect(last.card.remaining).toBe(THRESHOLD - i);
      }
    }

    // The Nth stamp completes the card.
    expect(last!.rewardGranted).toBe(true);
    expect(last!.card.stamps).toBe(0); // reset
    expect(last!.card.rewardsEarned).toBe(1);
    expect(last!.card.remaining).toBe(THRESHOLD);
  });

  it('rejects a NON-ADMIN caller before any write', async () => {
    const { user, code } = await seedCustomer(store);
    await expect(
      grantStampByCode(store, user, { code, idempotencyKey: 'x' }, THRESHOLD),
    ).rejects.toBeInstanceOf(ForbiddenError);

    // The card must be untouched.
    const after = await getMyCard(store, user, THRESHOLD);
    expect(after.stamps).toBe(0);
  });

  it('is idempotent: a repeated key (double scan) grants only one stamp', async () => {
    const admin = await seedAdmin(store);
    const { user, code } = await seedCustomer(store);

    const first = await grantStampByCode(
      store,
      admin,
      { code, idempotencyKey: 'same-key' },
      THRESHOLD,
    );
    const second = await grantStampByCode(
      store,
      admin,
      { code, idempotencyKey: 'same-key' },
      THRESHOLD,
    );

    expect(first.alreadyApplied).toBe(false);
    expect(second.alreadyApplied).toBe(true);

    const view = await getMyCard(store, user, THRESHOLD);
    expect(view.stamps).toBe(1); // NOT 2
  });

  it('rejects an unknown card code', async () => {
    const admin = await seedAdmin(store);
    await expect(
      grantStampByCode(store, admin, { code: 'LOY-XXXX-YYYY', idempotencyKey: 'k' }, THRESHOLD),
    ).rejects.toBeInstanceOf(NotFoundError);
  });
});
