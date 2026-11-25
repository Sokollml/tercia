"""XP awarding with cooldown / anti-abuse — pure logic and DB integration."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from bot.db import Chat, Event, Member
from bot.services.members import award_message_xp
from bot.xp import XpSettings, evaluate_message


# --- pure logic -------------------------------------------------------------

def _settings():
    return XpSettings(
        xp_per_message=5,
        cooldown_sec=60,
        min_message_len=3,
        antiflood_window_sec=5,
    )


def test_first_message_awards_xp():
    d = evaluate_message(
        text="hello there",
        is_command=False,
        is_sticker=False,
        now=datetime(2026, 1, 1, 12, 0, 0),
        last_xp_at=None,
        settings=_settings(),
    )
    assert d.awarded is True
    assert d.xp == 5
    assert d.reason == "ok"


def test_second_message_in_cooldown_gives_no_xp():
    now = datetime(2026, 1, 1, 12, 0, 0)
    last = now - timedelta(seconds=30)  # within 60s cooldown
    d = evaluate_message(
        text="another message",
        is_command=False,
        is_sticker=False,
        now=now,
        last_xp_at=last,
        settings=_settings(),
    )
    assert d.awarded is False
    assert d.reason == "cooldown"
    assert d.xp == 0


def test_message_after_cooldown_awards_again():
    now = datetime(2026, 1, 1, 12, 0, 0)
    last = now - timedelta(seconds=61)
    d = evaluate_message(
        text="ok now again",
        is_command=False,
        is_sticker=False,
        now=now,
        last_xp_at=last,
        settings=_settings(),
    )
    assert d.awarded is True


def test_short_message_rejected():
    d = evaluate_message(
        text="hi",
        is_command=False,
        is_sticker=False,
        now=datetime(2026, 1, 1, 12, 0, 0),
        last_xp_at=None,
        settings=_settings(),
    )
    assert d.awarded is False
    assert d.reason == "too_short"


def test_command_and_sticker_ignored():
    s = _settings()
    now = datetime(2026, 1, 1, 12, 0, 0)
    assert evaluate_message(text="/top", is_command=True, is_sticker=False, now=now, last_xp_at=None, settings=s).reason == "command"
    assert evaluate_message(text=None, is_command=False, is_sticker=True, now=now, last_xp_at=None, settings=s).reason == "sticker"


def test_antiflood_window():
    now = datetime(2026, 1, 1, 12, 0, 0)
    last = now - timedelta(seconds=2)  # within 5s antiflood
    d = evaluate_message(
        text="spam spam", is_command=False, is_sticker=False, now=now, last_xp_at=last, settings=_settings()
    )
    assert d.reason == "flood"


def test_disabled_module():
    d = evaluate_message(
        text="hello world", is_command=False, is_sticker=False,
        now=datetime(2026, 1, 1, 12, 0, 0), last_xp_at=None, settings=_settings(), enabled=False,
    )
    assert d.reason == "disabled"


# --- DB integration ---------------------------------------------------------

@pytest.mark.asyncio
async def test_award_persists_and_respects_cooldown(session):
    chat = Chat(id=-100, title="Test", xp_per_message=5, xp_cooldown_sec=60,
                min_message_len=3, antiflood_window_sec=5)
    member = Member(chat_id=-100, user_id=1, username="alice")
    session.add_all([chat, member])
    await session.flush()

    t0 = datetime(2026, 1, 1, 12, 0, 0)

    r1 = await award_message_xp(session, chat, member, text="hello world",
                                is_command=False, is_sticker=False, now=t0)
    assert r1.awarded is True
    assert member.xp == 5

    # 30s later — still inside cooldown, no XP
    r2 = await award_message_xp(session, chat, member, text="second message",
                                is_command=False, is_sticker=False, now=t0 + timedelta(seconds=30))
    assert r2.awarded is False
    assert member.xp == 5

    # 61s later — XP again
    r3 = await award_message_xp(session, chat, member, text="third message",
                                is_command=False, is_sticker=False, now=t0 + timedelta(seconds=61))
    assert r3.awarded is True
    assert member.xp == 10

    await session.flush()
    events = (await session.execute(Event.__table__.select())).fetchall()
    # only two XP events logged
    xp_events = [e for e in events if e.type == "xp"]
    assert len(xp_events) == 2
