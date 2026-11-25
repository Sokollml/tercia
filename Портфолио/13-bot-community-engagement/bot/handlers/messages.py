"""Catch-all message handler: XP accrual with anti-abuse."""
from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.i18n import t
from bot.services.members import award_message_xp, get_or_create_chat, get_or_create_member

log = logging.getLogger(__name__)
router = Router(name="messages")


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def on_group_message(message: Message, session: AsyncSession) -> None:
    user = message.from_user
    if user is None or user.is_bot:
        return

    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    if not chat.xp_enabled:
        return

    member = await get_or_create_member(
        session, chat.id, user.id, user.username or "", user.full_name or ""
    )

    text = message.text or message.caption or ""
    is_command = bool(message.text and message.text.startswith("/"))
    is_sticker = message.sticker is not None or message.animation is not None

    result = await award_message_xp(
        session,
        chat,
        member,
        text=text,
        is_command=is_command,
        is_sticker=is_sticker,
        lang=chat.lang,
    )

    if not result.awarded:
        return

    name = user.username and f"@{user.username}" or user.full_name
    try:
        if result.leveled_up:
            await message.answer(
                t("levelup", chat.lang, name=name, level=result.new_level, rank=result.new_rank)
            )
        if result.streak_milestone:
            await message.answer(
                t("streak_badge", chat.lang, name=name, streak=result.streak)
            )
    except Exception as exc:  # pragma: no cover - network
        log.warning("reward message failed: %s", exc)
