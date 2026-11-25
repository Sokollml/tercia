"""Warnings -> auto-mute escalation, exercised through the repository.

Mirrors the /warn handler's decision path without the aiogram layer.
"""
from __future__ import annotations

from app.moderation import now_ts, should_mute

CHAT = -1001
USER = 555
ADMIN = 1


async def test_warns_reach_limit_triggers_mute(repo):
    row = await repo.ensure_chat(CHAT, "Test")
    warn_limit = int(row["warn_limit"])  # default 3
    assert warn_limit == 3

    muted = False
    for i in range(1, warn_limit + 1):
        await repo.add_warning(CHAT, USER, ADMIN, reason="r%d" % i)
        count = await repo.count_active_warnings(CHAT, USER)
        assert count == i
        if should_mute(count, warn_limit):
            muted = True
            until = now_ts() + int(row["mute_duration"])
            await repo.add_mute(CHAT, USER, until, admin_id=0, reason="warn_limit")
            await repo.reset_warnings(CHAT, USER)

    # Threshold reached on the 3rd warning.
    assert muted is True
    # Warnings reset after auto-mute.
    assert await repo.count_active_warnings(CHAT, USER) == 0
    # An active mute now exists.
    active = await repo.active_mute(CHAT, USER)
    assert active is not None
    assert int(active["active"]) == 1


async def test_no_mute_below_threshold(repo):
    await repo.ensure_chat(CHAT, "Test")
    await repo.add_warning(CHAT, USER, ADMIN)
    await repo.add_warning(CHAT, USER, ADMIN)
    count = await repo.count_active_warnings(CHAT, USER)
    assert count == 2
    assert should_mute(count, 3) is False
    assert await repo.active_mute(CHAT, USER) is None


async def test_action_log_records_events(repo):
    await repo.ensure_chat(CHAT, "Test")
    await repo.log_action(CHAT, "warn", actor_id=ADMIN, target_id=USER, details="spam")
    await repo.log_action(CHAT, "mute", actor_id=0, target_id=USER)
    actions = await repo.recent_actions(CHAT, limit=10)
    assert len(actions) == 2
    # Most recent first.
    assert actions[0]["action"] == "mute"
    assert actions[1]["action"] == "warn"
