"""Weekly leaderboard calculation from the events log."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from bot.db import Event, Member
from bot.services.leaderboard import alltime_top, member_position, week_start, weekly_top


def test_week_start_is_monday_midnight():
    # 2026-01-01 is a Thursday
    ws = week_start(datetime(2026, 1, 1, 15, 30))
    assert ws.weekday() == 0  # Monday
    assert (ws.hour, ws.minute, ws.second) == (0, 0, 0)
    assert ws.date() == datetime(2025, 12, 29).date()


@pytest.mark.asyncio
async def test_weekly_top_sums_only_current_week(session):
    chat_id = -100
    session.add_all([
        Member(chat_id=chat_id, user_id=1, username="alice"),
        Member(chat_id=chat_id, user_id=2, username="bob"),
        Member(chat_id=chat_id, user_id=3, username="carol"),
    ])

    now = datetime(2026, 1, 8, 12, 0, 0)  # a Thursday
    ws = week_start(now)

    # In-week events
    session.add_all([
        Event(chat_id=chat_id, user_id=1, type="xp", xp=5, created_at=ws + timedelta(hours=1)),
        Event(chat_id=chat_id, user_id=1, type="xp", xp=5, created_at=ws + timedelta(hours=2)),
        Event(chat_id=chat_id, user_id=2, type="xp", xp=5, created_at=ws + timedelta(hours=3)),
        # a non-xp event should be ignored
        Event(chat_id=chat_id, user_id=2, type="levelup", xp=0, created_at=ws + timedelta(hours=3)),
        # last week's event should be excluded
        Event(chat_id=chat_id, user_id=3, type="xp", xp=100, created_at=ws - timedelta(days=2)),
    ])
    await session.flush()

    rows = await weekly_top(session, chat_id, now=now, limit=10)
    # carol excluded (old week); alice 10, bob 5
    assert [(r.name, r.value) for r in rows] == [("alice", 10), ("bob", 5)]
    assert rows[0].position == 1
    assert rows[1].position == 2


@pytest.mark.asyncio
async def test_alltime_top_and_position(session):
    chat_id = -100
    session.add_all([
        Member(chat_id=chat_id, user_id=1, username="alice", xp=100),
        Member(chat_id=chat_id, user_id=2, username="bob", xp=250),
        Member(chat_id=chat_id, user_id=3, username="carol", xp=50),
    ])
    await session.flush()

    rows = await alltime_top(session, chat_id, limit=10)
    assert [r.name for r in rows] == ["bob", "alice", "carol"]

    assert await member_position(session, chat_id, 2) == 1  # bob highest
    assert await member_position(session, chat_id, 1) == 2
    assert await member_position(session, chat_id, 3) == 3
    assert await member_position(session, chat_id, 999) == 0  # unknown
