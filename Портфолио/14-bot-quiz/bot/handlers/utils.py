"""Shared helpers for handlers."""
from __future__ import annotations

from typing import Optional

from aiogram.types import User

from .. import db as repo
from ..config import Settings
from ..i18n import normalize_lang


async def resolve_lang(
    database: repo.Database,
    settings: Settings,
    chat_id: int,
    user: Optional[User] = None,
) -> str:
    """Best-effort language for a chat.

    Group chats keep an explicit per-chat language; in private chats we fall
    back to the user's Telegram client language, then the configured default.
    """
    async with database.session() as session:
        row = await repo.get_chat_lang(session, chat_id, "")
    if row:
        return normalize_lang(row)
    if user is not None and user.language_code:
        return normalize_lang(user.language_code[:2])
    return normalize_lang(settings.default_lang)


def display_name(user: Optional[User]) -> Optional[str]:
    """A short, human-friendly name for storing alongside a score."""
    if user is None:
        return None
    if user.username:
        return "@" + user.username
    return user.full_name or None
