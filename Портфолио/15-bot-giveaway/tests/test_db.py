"""Integration tests for the SQLite database layer + draw reproducibility.

These use an on-disk temp SQLite file (each test gets its own) so the
schema, UNIQUE constraints and referral aggregation are exercised for real.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bot import logic
from bot.db import Database


@pytest.fixture
async def db(tmp_path):
    database = Database("sqlite", str(tmp_path / "test.db"))
    await database.connect()
    try:
        yield database
    finally:
        await database.close()


async def _make_giveaway(db: Database, *, seed="fixed-seed", winners=1, points_per_ref=1):
    ends = datetime.now(timezone.utc) + timedelta(hours=1)
    return await db.create_giveaway(
        chat_id=-100,
        creator_id=1,
        prize="Prize",
        description="",
        winners_count=winners,
        points_per_ref=points_per_ref,
        required_channel=None,
        seed=seed,
        ends_at=ends,
    )


# --------------------------------------------------------------------------
# Anti-abuse: one account = one participation.
# --------------------------------------------------------------------------
async def test_duplicate_participation_blocked(db):
    gid = await _make_giveaway(db)

    assert await db.add_participant(gid, 500, "alice", "Alice") is True
    # Second attempt by the same user -> rejected.
    assert await db.add_participant(gid, 500, "alice", "Alice") is False
    assert await db.count_participants(gid) == 1


async def test_participants_are_isolated_per_giveaway(db):
    g1 = await _make_giveaway(db)
    g2 = await _make_giveaway(db)
    assert await db.add_participant(g1, 7, None, None) is True
    # Same user may join a *different* giveaway.
    assert await db.add_participant(g2, 7, None, None) is True
    assert await db.count_participants(g1) == 1
    assert await db.count_participants(g2) == 1


# --------------------------------------------------------------------------
# Referrals: dedupe per invited user, ignore self-invite, correct counts.
# --------------------------------------------------------------------------
async def test_referral_counting(db):
    gid = await _make_giveaway(db)
    for uid in (10, 20, 30, 40):
        await db.add_participant(gid, uid, None, None)

    assert await db.add_referral(gid, 10, 20) is True
    assert await db.add_referral(gid, 10, 30) is True
    # Same invited user again (even by a different inviter) -> ignored.
    assert await db.add_referral(gid, 10, 20) is False
    assert await db.add_referral(gid, 40, 20) is False
    # Self-invite -> ignored.
    assert await db.add_referral(gid, 10, 10) is False

    assert await db.count_referrals(gid, 10) == 2
    assert await db.count_referrals(gid, 40) == 0
    assert await db.count_all_referrals(gid) == 2


async def test_participants_with_tickets_reflects_referrals(db):
    gid = await _make_giveaway(db, points_per_ref=3)
    for uid in (1, 2, 3, 4):
        await db.add_participant(gid, uid, None, None)
    # User 1 invited two people.
    await db.add_referral(gid, 1, 2)
    await db.add_referral(gid, 1, 3)

    pool = dict(await db.participants_with_tickets(gid, points_per_ref=3))
    assert pool[1] == 1 + 2 * 3  # base 1 + two referrals * 3
    assert pool[2] == 1
    assert pool[4] == 1


# --------------------------------------------------------------------------
# End-to-end: the stored seed makes the draw reproducible from the DB.
# --------------------------------------------------------------------------
async def test_draw_reproducible_from_stored_seed(db):
    seed = logic.generate_seed()
    gid = await _make_giveaway(db, seed=seed, winners=3, points_per_ref=1)
    for uid in range(1, 51):
        await db.add_participant(gid, uid, None, None)

    stored = await db.get_giveaway(gid)
    pool = await db.participants_with_tickets(gid, int(stored["points_per_ref"]))

    winners_a = logic.select_winners(pool, stored["seed"], int(stored["winners_count"]))
    # Anyone can recompute later with the same stored seed + participants.
    winners_b = logic.select_winners(pool, stored["seed"], int(stored["winners_count"]))
    assert winners_a == winners_b
    assert logic.verify_draw(pool, stored["seed"], 3, winners_a) is True


async def test_finish_giveaway_persists_winners(db):
    gid = await _make_giveaway(db, winners=2)
    for uid in (1, 2, 3):
        await db.add_participant(gid, uid, None, None)
    await db.finish_giveaway(gid, [1, 2])

    row = await db.get_giveaway(gid)
    assert row["status"] == "finished"
    assert "1" in row["winners"] and "2" in row["winners"]
    assert row["finished_at"] is not None


async def test_due_giveaways_detects_expired(db):
    # Past end time -> due.
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    gid = await db.create_giveaway(
        chat_id=-100, creator_id=1, prize="P", description="",
        winners_count=1, points_per_ref=1, required_channel=None,
        seed="s", ends_at=past,
    )
    due = await db.due_giveaways()
    assert any(int(g["id"]) == gid for g in due)
