"""Antispam and antiflood message filtering for group chats.

Registered LAST so command routers get first pick; this handler only sees
ordinary member messages.
"""
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from .. import i18n, utils
from ..moderation import (
    FloodTracker,
    format_duration,
    has_link,
    matched_stopword,
    now_ts,
    parse_stopwords,
)
from ..repository import Repository

log = logging.getLogger("moderation.handlers.antispam")
router = Router(name="antispam")


def _message_text(message: Message) -> str:
    return message.text or message.caption or ""


def _spam_reason(message: Message, row: dict) -> Optional[str]:
    """Return a short reason string if the message violates a filter."""
    text = _message_text(message)
    if int(row.get("filter_forwards") or 0):
        # forward_origin (Bot API 7+) or the legacy forward_date fallback.
        if getattr(message, "forward_origin", None) or message.forward_date:
            return "forward"
    if int(row.get("filter_links") or 0) and has_link(text):
        return "link"
    if int(row.get("filter_stopwords") or 0):
        word = matched_stopword(text, parse_stopwords(row.get("stopwords") or ""))
        if word:
            return "stopword"
    return None


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    ~F.text.startswith("/"),
)
async def on_group_message(
    message: Message, bot: Bot, repo: Repository, flood: FloodTracker
) -> None:
    if message.from_user is None or message.from_user.is_bot:
        return
    chat_id = message.chat.id
    user_id = message.from_user.id

    row = await repo.ensure_chat(chat_id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang

    # Never moderate admins / owners.
    if await utils.is_user_admin(bot, repo.cfg, chat_id, user_id):
        return

    # ---- content filters (link / forward / stop-word) ----
    reason = _spam_reason(message, row)
    if reason is not None:
        deleted = await utils.delete_message_safe(bot, chat_id, message.message_id)
        await repo.log_action(chat_id, "spam_delete", target_id=user_id, details=reason)
        if deleted:
            log.info("deleted spam (%s) from %s in %s", reason, user_id, chat_id)
        return

    # ---- antiflood (sliding window) ----
    if int(row.get("antiflood_enabled") or 0):
        flood.limit = int(row.get("antiflood_limit") or flood.limit)
        flood.window = int(row.get("antiflood_window") or flood.window)
        if flood.hit(chat_id, user_id):
            duration = int(row.get("mute_duration") or repo.cfg.mute_duration)
            until = now_ts() + duration
            if await utils.restrict_user(bot, chat_id, user_id, until_ts=until):
                await repo.add_mute(chat_id, user_id, until, admin_id=0, reason="flood")
                await repo.log_action(chat_id, "flood_mute", target_id=user_id)
                flood.reset(chat_id, user_id)
                await message.answer(
                    i18n.t(
                        lang,
                        "flood_muted",
                        name=utils.mention(message.from_user),
                        duration=format_duration(duration, lang),
                    )
                )
