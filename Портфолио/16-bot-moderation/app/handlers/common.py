"""General commands: /start, /help, /rules, /id, /lang, /setrules, /setwelcome."""
from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from .. import i18n
from ..config import Config
from ..repository import Repository
from ..utils import is_user_admin

log = logging.getLogger("moderation.handlers.common")
router = Router(name="common")


async def _chat_lang(repo: Repository, message: Message) -> str:
    if message.chat.type == ChatType.PRIVATE:
        return repo.cfg.default_lang
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    return row.get("lang") or repo.cfg.default_lang


@router.message(Command("start"))
async def cmd_start(message: Message, repo: Repository) -> None:
    lang = repo.cfg.default_lang
    await message.answer(i18n.t(lang, "start"))


@router.message(Command("help"))
async def cmd_help(message: Message, repo: Repository) -> None:
    lang = await _chat_lang(repo, message)
    await message.answer(i18n.t(lang, "help"))


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    await message.answer("chat_id: <code>%d</code>\nuser_id: <code>%d</code>" % (message.chat.id, uid))


@router.message(Command("rules"))
async def cmd_rules(message: Message, repo: Repository) -> None:
    if message.chat.type == ChatType.PRIVATE:
        await message.answer(i18n.default_rules(repo.cfg.default_lang))
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    text = (row.get("rules_text") or "").strip()
    if not text:
        text = i18n.default_rules(lang)
    await message.answer(text)


@router.message(Command("lang"))
async def cmd_lang(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    if message.chat.type == ChatType.PRIVATE:
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return
    arg = (command.args or "").strip().lower()
    if arg not in ("ru", "en"):
        await message.answer(i18n.t(lang, "lang_usage"))
        return
    await repo.update_setting(message.chat.id, "lang", arg)
    await message.answer(i18n.t(arg, "lang_updated"))


@router.message(Command("setrules"))
async def cmd_setrules(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    if message.chat.type == ChatType.PRIVATE:
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return
    text = (command.args or "").strip()
    await repo.update_setting(message.chat.id, "rules_text", text)
    await message.answer(i18n.t(lang, "rules_updated"))


@router.message(Command("setwelcome"))
async def cmd_setwelcome(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    if message.chat.type == ChatType.PRIVATE:
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return
    text = (command.args or "").strip()
    await repo.update_setting(message.chat.id, "welcome_text", text)
    await message.answer(i18n.t(lang, "welcome_updated"))
