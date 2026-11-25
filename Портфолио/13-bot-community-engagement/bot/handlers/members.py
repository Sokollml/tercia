"""Welcome new members."""
from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Event
from bot.i18n import t
from bot.services.members import get_or_create_chat, get_or_create_member

log = logging.getLogger(__name__)
router = Router(name="members")


@router.message(F.new_chat_members)
async def on_new_members(message: Message, session: AsyncSession) -> None:
    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    if not chat.welcome_enabled:
        return
    lang = chat.lang

    for user in message.new_chat_members or []:
        if user.is_bot:
            continue
        name = user.full_name or (user.username or str(user.id))
        await get_or_create_member(
            session, chat.id, user.id, user.username or "", user.full_name or ""
        )
        session.add(Event(chat_id=chat.id, user_id=user.id, type="join", xp=0))

        custom = chat.welcome_text_ru if lang == "ru" else chat.welcome_text_en
        if custom:
            text = custom.replace("{name}", name)
        else:
            text = t("welcome_default", lang, name=name)
        try:
            await message.answer(text)
        except Exception as exc:  # pragma: no cover - network
            log.warning("welcome send failed: %s", exc)
