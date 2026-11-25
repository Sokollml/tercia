"""Spaced-repetition scheduling (SM-2 lite / Leitner hybrid).

Pure, side-effect-free logic so it is trivial to unit-test.  A mistake collected
during a dialog becomes a review item.  Each time the user answers a mini-quiz
about that mistake we call :func:`review` with the outcome:

* on **success** the repetition streak grows and the next interval expands;
* on **failure** the streak resets to zero and the interval collapses to the
  minimum, so the item comes back quickly.

Timestamps are UNIX epoch **seconds** in UTC, matching the rest of the app.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

DAY_SECONDS = 86400

# Leitner-style base intervals (in days) for the first few successful reviews.
# Beyond the last box we scale the previous interval by the ease factor.
BASE_INTERVALS_DAYS = (1, 3, 7)

MIN_EASE = 1.3
DEFAULT_EASE = 2.5
EASE_BONUS = 0.1   # applied on success
EASE_PENALTY = 0.2  # applied on failure


@dataclass(frozen=True)
class SrsState:
    """The persisted scheduling state for a single mistake."""

    repetitions: int = 0          # consecutive successful reviews
    interval_days: int = 0        # current spacing in days
    ease: float = DEFAULT_EASE    # SM-2 ease factor


def _next_interval_days(state: SrsState) -> int:
    """Interval (days) for the *upcoming* review, given the streak so far."""
    reps = state.repetitions  # streak *before* this success is counted
    if reps < len(BASE_INTERVALS_DAYS):
        return BASE_INTERVALS_DAYS[reps]
    # Past the fixed boxes: expand geometrically by the ease factor.
    grown = int(round(max(state.interval_days, BASE_INTERVALS_DAYS[-1]) * state.ease))
    return max(grown, BASE_INTERVALS_DAYS[-1] + 1)


def review(state: SrsState, success: bool) -> SrsState:
    """Return the new :class:`SrsState` after a review with the given outcome.

    Guarantees exercised by the test-suite:

    * a run of successes yields **strictly non-decreasing** intervals that grow;
    * any failure resets ``repetitions`` to ``0`` and shrinks the interval back
      to the first Leitner box.
    """
    if not success:
        return SrsState(
            repetitions=0,
            interval_days=BASE_INTERVALS_DAYS[0],
            ease=max(MIN_EASE, state.ease - EASE_PENALTY),
        )

    interval = _next_interval_days(state)
    return SrsState(
        repetitions=state.repetitions + 1,
        interval_days=interval,
        ease=min(3.0, state.ease + EASE_BONUS),
    )


def next_review_ts(state: SrsState, now_ts: int) -> int:
    """Epoch (seconds) at which the item should next surface."""
    return now_ts + state.interval_days * DAY_SECONDS


def schedule(
    repetitions: int,
    interval_days: int,
    ease: float,
    success: bool,
    now_ts: int,
) -> dict:
    """Convenience wrapper used by the repository layer.

    Takes the raw columns stored for a mistake plus the review outcome and
    returns the updated columns (as a dict) including the new ``next_review``.
    """
    new_state = review(
        SrsState(repetitions=repetitions, interval_days=interval_days, ease=ease),
        success,
    )
    return {
        "repetitions": new_state.repetitions,
        "interval_days": new_state.interval_days,
        "ease": new_state.ease,
        "next_review": next_review_ts(new_state, now_ts),
    }


def initial_next_review(now_ts: int, delay_days: Optional[int] = None) -> int:
    """When a brand-new mistake should first be reviewed (default: 1 day)."""
    days = BASE_INTERVALS_DAYS[0] if delay_days is None else delay_days
    return now_ts + days * DAY_SECONDS
