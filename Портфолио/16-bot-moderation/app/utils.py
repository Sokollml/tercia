"""Telegram-facing helpers: permission checks and safe action wrappers.

These are the only functions that talk to the Bot API directly (besides
handlers), so the pure logic in :mod:`app.moderation` stays testable.
"""
from __future__ import annotations

import html
import logging
from typing import Optional

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatPermissions, User

from .config import Config

log = logging.getLogger("moderation.utils")

_ADMIN_STATUSES = {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}

# All permissions revoked — used to mute a user.
MUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

# A permissive default restoring normal chat abilities on unmute.
UNMUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
)


def display_name(user: Optional[User]) -> str:
    """Safe, HTML-escaped display name for a user (or a placeholder)."""
    if user is None:
        return "user"
    name = user.full_name or (("@" + user.username) if user.username else str(user.id))
    return html.escape(name)


def mention(user: Optional[User]) -> str:
    """An HTML mention link so notices ping the user without exposing raw ids."""
    if user is None:
        return "user"
    return '<a href="tg://user?id=%d">%s</a>' % (user.id, display_name(user))


async def is_user_admin(bot: Bot, cfg: Config, chat_id: int, user_id: int) -> bool:
    """True for global bot owners and Telegram chat admins/creators."""
    if cfg.is_owner(user_id):
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover - network
        log.warning("get_chat_member failed: %s", exc)
        return False
    return member.status in _ADMIN_STATUSES


async def bot_can_restrict(bot: Bot, chat_id: int) -> bool:
    """Whether the bot is an admin able to restrict/ban in this chat."""
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.warning("bot self get_chat_member failed: %s", exc)
        return False
    if member.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    # can_restrict_members governs both mute and ban.
    return bool(getattr(member, "can_restrict_members", False))


async def restrict_user(bot: Bot, chat_id: int, user_id: int, until_ts: int = 0) -> bool:
    """Mute a user until ``until_ts`` (0 = permanent). Returns success."""
    try:
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=MUTED_PERMISSIONS,
            until_date=until_ts or None,
        )
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.warning("restrict_user failed: %s", exc)
        return False


async def unrestrict_user(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        await bot.restrict_chat_member(
            chat_id, user_id, permissions=UNMUTED_PERMISSIONS
        )
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.warning("unrestrict_user failed: %s", exc)
        return False


async def ban_user(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        await bot.ban_chat_member(chat_id, user_id)
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.warning("ban_user failed: %s", exc)
        return False


async def unban_user(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.warning("unban_user failed: %s", exc)
        return False


async def kick_user(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Kick = ban then immediately unban so the user may rejoin later."""
    ok = await ban_user(bot, chat_id, user_id)
    if ok:
        await unban_user(bot, chat_id, user_id)
    return ok


async def delete_message_safe(bot: Bot, chat_id: int, message_id: int) -> bool:
    try:
        await bot.delete_message(chat_id, message_id)
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as exc:  # pragma: no cover
        log.debug("delete_message failed: %s", exc)
        return False
