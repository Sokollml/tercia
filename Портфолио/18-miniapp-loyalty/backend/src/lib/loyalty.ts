/**
 * Pure loyalty-card business logic.
 *
 * Kept free of any database or HTTP concerns so it can be unit-tested in
 * isolation and reasoned about easily. The route layer calls these functions
 * and persists the result.
 */

export interface CardState {
  /** Stamps collected in the *current* (not-yet-rewarded) cycle. */
  stamps: number;
  /** Total number of rewards the customer has already earned overall. */
  rewardsEarned: number;
}

export interface StampOutcome {
  /** New card state after applying the stamp. */
  next: CardState;
  /** True when this stamp completed a card and produced a reward. */
  rewardGranted: boolean;
  /** Stamps still needed for the next reward (0 right after a reward). */
  remaining: number;
}

/**
 * Apply a single stamp to a card.
 *
 * When the stamp count reaches `threshold`, a reward is granted and the
 * per-cycle counter resets to 0. `rewardsEarned` is a monotonic lifetime
 * total used for statistics.
 *
 * @throws if threshold is not a positive integer.
 */
export function applyStamp(state: CardState, threshold: number): StampOutcome {
  if (!Number.isInteger(threshold) || threshold < 1) {
    throw new Error(`Invalid reward threshold: ${threshold}`);
  }

  const stamps = state.stamps + 1;

  if (stamps >= threshold) {
    // Card completed → reward granted, counter resets for a fresh cycle.
    return {
      next: { stamps: 0, rewardsEarned: state.rewardsEarned + 1 },
      rewardGranted: true,
      remaining: threshold,
    };
  }

  return {
    next: { stamps, rewardsEarned: state.rewardsEarned },
    rewardGranted: false,
    remaining: threshold - stamps,
  };
}

/** How many stamps remain before the next reward, given a current state. */
export function stampsRemaining(state: CardState, threshold: number): number {
  return Math.max(0, threshold - state.stamps);
}
