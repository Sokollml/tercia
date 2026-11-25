"""Integration tests for the data-access layer against in-memory SQLite.

These exercise the SRS wiring end-to-end (add a mistake, review it, watch
``next_review`` grow on success and reset on failure) plus the daily quota.
"""
from __future__ import annotations

import pytest

from app import srs

NOW = 1_700_000_000


@pytest.mark.asyncio
async def test_ensure_user_is_idempotent(repo):
    u1 = await repo.ensure_user(1, "ru", NOW)
    u2 = await repo.ensure_user(1, "en", NOW)  # second call must not overwrite
    assert u1["id"] == 1
    assert u2["ui_lang"] == "ru"  # unchanged


@pytest.mark.asyncio
async def test_add_mistake_sets_initial_next_review(repo):
    await repo.ensure_user(1, "ru", NOW)
    mid = await repo.add_mistake(1, "i go", "I went", "past tense", "tense", NOW)
    row = await repo.get_mistake(mid)
    assert row["original"] == "i go"
    assert row["corrected"] == "I went"
    assert row["repetitions"] == 0
    assert row["next_review"] == NOW + srs.DAY_SECONDS


@pytest.mark.asyncio
async def test_next_review_grows_with_successes(repo):
    await repo.ensure_user(1, "ru", NOW)
    mid = await repo.add_mistake(1, "a", "b", "", "grammar", NOW)

    previous = 0
    for step in range(4):
        row = await repo.apply_review(mid, success=True, now_ts=NOW)
        interval = row["next_review"] - NOW
        assert row["repetitions"] == step + 1
        assert interval > previous  # strictly growing across successes
        previous = interval
    assert row["times_correct"] == 4
    assert row["times_wrong"] == 0


@pytest.mark.asyncio
async def test_failure_resets_next_review(repo):
    await repo.ensure_user(1, "ru", NOW)
    mid = await repo.add_mistake(1, "a", "b", "", "grammar", NOW)

    # Grow a streak.
    for _ in range(4):
        await repo.apply_review(mid, success=True, now_ts=NOW)
    grown = await repo.get_mistake(mid)
    assert grown["next_review"] - NOW > srs.DAY_SECONDS

    # A wrong answer collapses the schedule back to one day.
    reset = await repo.apply_review(mid, success=False, now_ts=NOW)
    assert reset["repetitions"] == 0
    assert reset["next_review"] == NOW + srs.DAY_SECONDS
    assert reset["times_wrong"] == 1


@pytest.mark.asyncio
async def test_due_and_count_due(repo):
    await repo.ensure_user(1, "ru", NOW)
    await repo.add_mistake(1, "a", "b", "", "grammar", NOW)

    # Not due yet (first review is one day out).
    assert await repo.count_due(1, NOW) == 0
    # Due once we look one day later.
    later = NOW + srs.DAY_SECONDS + 1
    assert await repo.count_due(1, later) == 1
    due = await repo.due_mistakes(1, later)
    assert len(due) == 1


@pytest.mark.asyncio
async def test_top_error_types(repo):
    await repo.ensure_user(1, "ru", NOW)
    await repo.add_mistake(1, "a", "b", "", "tense", NOW)
    await repo.add_mistake(1, "c", "d", "", "tense", NOW)
    await repo.add_mistake(1, "e", "f", "", "article", NOW)
    top = await repo.top_error_types(1)
    assert top[0]["error_type"] == "tense"
    assert top[0]["n"] == 2


@pytest.mark.asyncio
async def test_daily_quota_consumes_and_blocks(repo):
    await repo.ensure_user(1, "ru", NOW)
    limit = 3
    for _ in range(limit):
        assert await repo.check_and_consume_quota(1, "2026-08-02", limit) is True
    # Fourth call in the same day is blocked.
    assert await repo.check_and_consume_quota(1, "2026-08-02", limit) is False
    assert await repo.remaining_quota(1, "2026-08-02", limit) == 0


@pytest.mark.asyncio
async def test_daily_quota_resets_next_day(repo):
    await repo.ensure_user(1, "ru", NOW)
    limit = 2
    assert await repo.check_and_consume_quota(1, "2026-08-02", limit) is True
    assert await repo.check_and_consume_quota(1, "2026-08-02", limit) is True
    assert await repo.check_and_consume_quota(1, "2026-08-02", limit) is False
    # New day → counter resets.
    assert await repo.check_and_consume_quota(1, "2026-08-03", limit) is True
    assert await repo.remaining_quota(1, "2026-08-03", limit) == 1


@pytest.mark.asyncio
async def test_premium_user_unlimited(repo):
    await repo.ensure_user(1, "ru", NOW)
    await repo.db.execute("UPDATE users SET is_premium = 1 WHERE id = ?", 1)
    for _ in range(100):
        assert await repo.check_and_consume_quota(1, "2026-08-02", 3) is True


@pytest.mark.asyncio
async def test_sessions_lifecycle(repo):
    await repo.ensure_user(1, "ru", NOW)
    sid = await repo.start_session(1, "dialog", NOW)
    await repo.bump_session(sid)
    await repo.bump_session(sid)
    await repo.end_session(sid, NOW + 100)
    row = await repo.db.fetchone("SELECT * FROM sessions WHERE id = ?", sid)
    assert row["messages"] == 2
    assert row["ended_at"] == NOW + 100
