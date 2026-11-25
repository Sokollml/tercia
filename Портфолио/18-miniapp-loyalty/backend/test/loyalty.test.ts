import { describe, expect, it } from 'vitest';
import { applyStamp, stampsRemaining } from '../src/lib/loyalty.js';

describe('applyStamp', () => {
  it('increments stamps below the threshold without a reward', () => {
    const out = applyStamp({ stamps: 0, rewardsEarned: 0 }, 8);
    expect(out.rewardGranted).toBe(false);
    expect(out.next.stamps).toBe(1);
    expect(out.remaining).toBe(7);
  });

  it('grants a reward and RESETS the counter on the Nth stamp', () => {
    // Card sits at 7/8; the 8th stamp completes it.
    const out = applyStamp({ stamps: 7, rewardsEarned: 0 }, 8);
    expect(out.rewardGranted).toBe(true);
    expect(out.next.stamps).toBe(0); // reset for the next cycle
    expect(out.next.rewardsEarned).toBe(1);
    expect(out.remaining).toBe(8);
  });

  it('walks a full cycle end-to-end: 8 stamps -> 1 reward, back to 0', () => {
    let state = { stamps: 0, rewardsEarned: 0 };
    let rewards = 0;
    for (let i = 0; i < 8; i++) {
      const out = applyStamp(state, 8);
      state = out.next;
      if (out.rewardGranted) rewards++;
    }
    expect(rewards).toBe(1);
    expect(state.stamps).toBe(0);
    expect(state.rewardsEarned).toBe(1);
  });

  it('supports multiple cycles', () => {
    let state = { stamps: 0, rewardsEarned: 0 };
    for (let i = 0; i < 24; i++) state = applyStamp(state, 8).next;
    expect(state.rewardsEarned).toBe(3);
    expect(state.stamps).toBe(0);
  });

  it('rejects an invalid threshold', () => {
    expect(() => applyStamp({ stamps: 0, rewardsEarned: 0 }, 0)).toThrow();
    expect(() => applyStamp({ stamps: 0, rewardsEarned: 0 }, 1.5)).toThrow();
  });
});

describe('stampsRemaining', () => {
  it('never returns a negative number', () => {
    expect(stampsRemaining({ stamps: 3, rewardsEarned: 0 }, 8)).toBe(5);
    expect(stampsRemaining({ stamps: 0, rewardsEarned: 0 }, 8)).toBe(8);
  });
});
