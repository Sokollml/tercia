"""Tests for the spaced-repetition scheduling core (app.srs).

The central guarantees:

* a streak of correct answers makes ``next_review`` grow monotonically;
* a single wrong answer resets the streak and pulls ``next_review`` back to the
  first (shortest) box.
"""
from __future__ import annotations

from app import srs
from app.srs import DAY_SECONDS, SrsState


def test_success_grows_repetitions_and_interval():
    state = SrsState()
    intervals = []
    for _ in range(6):
        state = srs.review(state, success=True)
        intervals.append(state.interval_days)

    # Repetitions increment by one each success.
    assert state.repetitions == 6
    # First three follow the fixed Leitner boxes.
    assert intervals[0] == 1
    assert intervals[1] == 3
    assert intervals[2] == 7
    # Intervals never shrink across a run of successes and eventually exceed 7.
    assert intervals == sorted(intervals)
    assert intervals[-1] > 7


def test_next_review_increases_with_each_success():
    now = 1_000_000
    state = SrsState()
    previous_delta = -1
    for _ in range(6):
        state = srs.review(state, success=True)
        delta = srs.next_review_ts(state, now) - now
        assert delta > 0
        assert delta >= previous_delta  # non-decreasing spacing
        previous_delta = delta


def test_failure_resets_streak_and_interval():
    # Build up a long streak first.
    state = SrsState()
    for _ in range(5):
        state = srs.review(state, success=True)
    assert state.repetitions == 5
    assert state.interval_days > 7

    # One failure collapses everything back to the first box.
    failed = srs.review(state, success=False)
    assert failed.repetitions == 0
    assert failed.interval_days == srs.BASE_INTERVALS_DAYS[0]  # == 1
    # And the next review is only one day out, not weeks.
    now = 500_000
    assert srs.next_review_ts(failed, now) == now + DAY_SECONDS


def test_failure_lowers_ease_success_raises_it():
    state = SrsState(repetitions=3, interval_days=7, ease=2.5)
    assert srs.review(state, success=False).ease < 2.5
    assert srs.review(state, success=True).ease > 2.5


def test_ease_never_below_minimum():
    state = SrsState(ease=srs.MIN_EASE)
    for _ in range(10):
        state = srs.review(state, success=False)
    assert state.ease >= srs.MIN_EASE


def test_schedule_wrapper_matches_review():
    now = 2_000_000
    out = srs.schedule(repetitions=0, interval_days=0, ease=2.5, success=True, now_ts=now)
    assert out["repetitions"] == 1
    assert out["interval_days"] == 1
    assert out["next_review"] == now + DAY_SECONDS

    # A failure from a high streak resets in the wrapper too.
    out2 = srs.schedule(repetitions=5, interval_days=30, ease=2.5, success=False, now_ts=now)
    assert out2["repetitions"] == 0
    assert out2["interval_days"] == 1
    assert out2["next_review"] == now + DAY_SECONDS


def test_initial_next_review_default_one_day():
    now = 10_000
    assert srs.initial_next_review(now) == now + DAY_SECONDS
    assert srs.initial_next_review(now, delay_days=0) == now
