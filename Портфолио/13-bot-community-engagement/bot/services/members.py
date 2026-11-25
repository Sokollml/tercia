"""DB-backed member / XP operations built on the pure logic in bot.xp."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Chat, Event, Member
from bot.xp import (
    XpSettings,
    compute_streak,
    evaluate_message,
    level_for_xp,
    rank_for_level,
)


@dataclass
class AwardResult:
    awarded: bool
    reason: str
    xp_gained: int = 0
    leveled_up: bool = False
    new_level: int = 0
    new_rank: str = ""
    streak: int = 0
    streak_milestone: bool = False


def settings_from_chat(chat: Chat) -> XpSettings:
    return XpSettings(
        xp_per_message=chat.xp_per_message,
        cooldown_sec=chat.xp_cooldown_sec,
        min_message_len=chat.min_message_len,
        antiflood_window_sec=chat.antiflood_window_sec,
    )


async def get_or_create_chat(session: AsyncSession, chat_id: int, title: str = "", default_lang: str = "ru") -> Chat:
    chat = await session.get(Chat, chat_id)
    if chat is None:
        chat = Chat(id=chat_id, title=title or None, lang=default_lang)
        session.add(chat)
        await session.flush()
    elif title and chat.title != title:
        chat.title = title
    return chat


async def get_or_create_member(
    session: AsyncSession, chat_id: int, user_id: int, username: str = "", full_name: str = ""
) -> Member:
    member = await session.get(Member, {"chat_id": chat_id, "user_id": user_id})
    if member is None:
        member = Member(
            chat_id=chat_id,
            user_id=user_id,
            username=username or None,
            full_name=full_name or None,
        )
        session.add(member)
        await session.flush()
    else:
        if username:
            member.username = username
        if full_name:
            member.full_name = full_name
    return member


# streak milestones that unlock a badge
STREAK_MILESTONES = {3, 7, 14, 30, 60, 100}


async def award_message_xp(
    session: AsyncSession,
    chat: Chat,
    member: Member,
    *,
    text: Optional[str],
    is_command: bool,
    is_sticker: bool,
    now: Optional[datetime] = None,
    lang: str = "ru",
) -> AwardResult:
    """Evaluate a message, persist XP/level/streak changes and log an event."""
    now = now or datetime.utcnow()
    settings = settings_from_chat(chat)

    decision = evaluate_message(
        text=text,
        is_command=is_command,
        is_sticker=is_sticker,
        now=now,
        last_xp_at=member.last_xp_at,
        settings=settings,
        enabled=chat.xp_enabled,
    )

    # Streak is updated on any real (non-command/sticker) activity, even if XP
    # was on cooldown — showing up daily should count.
    result = AwardResult(awarded=False, reason=decision.reason)
    today = now.date()

    if not decision.awarded:
        return result

    old_level = member.level
    member.xp += decision.xp
    new_level = level_for_xp(member.xp)
    member.level = new_level
    member.last_xp_at = now

    new_streak = compute_streak(
        last_active_date=member.last_active_date,
        today=today,
        current_streak=member.streak,
    )
    member.streak = new_streak
    member.last_active_date = today

    session.add(
        Event(
            chat_id=chat.id,
            user_id=member.user_id,
            type="xp",
            xp=decision.xp,
            created_at=now,
        )
    )

    result.awarded = True
    result.xp_gained = decision.xp
    result.streak = new_streak
    result.streak_milestone = new_streak in STREAK_MILESTONES
    if new_level > old_level:
        result.leveled_up = True
        result.new_level = new_level
        result.new_rank = rank_for_level(new_level, lang)
        session.add(
            Event(chat_id=chat.id, user_id=member.user_id, type="levelup", xp=0, meta=str(new_level), created_at=now)
        )
    if result.streak_milestone:
        session.add(
            Event(chat_id=chat.id, user_id=member.user_id, type="streak", xp=0, meta=str(new_streak), created_at=now)
        )
    return result
