"""Common commands available to everyone: /start, /help, /lang."""
from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from .. import db as repo
from ..config import Settings
from ..i18n import SUPPORTED, normalize_lang, t
from .utils import resolve_lang

logger = logging.getLogger(__name__)
router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    await message.answer(t("start", lang))


@router.message(Command("help"))
async def cmd_help(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    text = t("help_user", lang)
    if message.from_user and settings.is_admin(message.from_user.id):
        text += t("help_admin", lang)
    await message.answer(text)


@router.message(Command("lang"))
async def cmd_lang(
    message: Message,
    command: CommandObject,
    database: repo.Database,
    settings: Settings,
) -> None:
    arg = (command.args or "").strip().lower()
    if arg not in SUPPORTED:
        lang = await resolve_lang(
            database, settings, message.chat.id, message.from_user
        )
        await message.answer(t("lang_usage", lang))
        return

    lang = normalize_lang(arg)
    async with database.session() as session:
        await repo.set_chat_lang(session, message.chat.id, lang)
    await message.answer(t("lang_set", lang))
