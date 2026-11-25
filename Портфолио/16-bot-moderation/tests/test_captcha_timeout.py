"""Captcha timeout -> newcomer is kicked when the deadline passes."""
from __future__ import annotations

from app.moderation import now_ts
from app.scheduler import enforce_captcha_timeouts

CHAT = -1002
USER = 777


async def test_expired_captcha_kicks_user(repo, fake_bot):
    await repo.ensure_chat(CHAT, "Test")
    # Deadline already in the past.
    past = now_ts() - 1
    await repo.add_pending(CHAT, USER, message_id=42, answer="7", deadline_ts=past)

    bot = fake_bot
    kicked = await enforce_captcha_timeouts(bot, repo, now=now_ts())

    assert kicked == 1
    # kick = ban then unban so the user may rejoin.
    assert (CHAT, USER) in bot.banned
    assert (CHAT, USER) in bot.unbanned
    # Challenge message deleted.
    assert (CHAT, 42) in bot.deleted
    # Pending record cleared.
    assert await repo.get_pending(CHAT, USER) is None
    # Action logged.
    actions = await repo.recent_actions(CHAT, limit=5)
    assert any(a["action"] == "captcha_timeout_kick" for a in actions)


async def test_unexpired_captcha_is_left_alone(repo, fake_bot):
    await repo.ensure_chat(CHAT, "Test")
    future = now_ts() + 60
    await repo.add_pending(CHAT, USER, message_id=1, answer="4", deadline_ts=future)

    bot = fake_bot
    kicked = await enforce_captcha_timeouts(bot, repo, now=now_ts())

    assert kicked == 0
    assert bot.banned == []
    assert await repo.get_pending(CHAT, USER) is not None


async def test_pending_replaced_on_reissue(repo):
    await repo.ensure_chat(CHAT, "Test")
    await repo.add_pending(CHAT, USER, message_id=1, answer="4", deadline_ts=now_ts() + 60)
    # Re-issuing replaces the previous pending row (UNIQUE chat+user).
    await repo.add_pending(CHAT, USER, message_id=2, answer="9", deadline_ts=now_ts() + 60)
    pending = await repo.get_pending(CHAT, USER)
    assert pending is not None
    assert pending["answer"] == "9"
    assert int(pending["message_id"]) == 2
