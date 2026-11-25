"""Admin commands: settings, toggles, welcome text, manual prompt, language."""
from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import Config
from bot.i18n import t
from bot.services.members import get_or_create_chat
from bot.services.prompts import pick_prompt

log = logging.getLogger(__name__)
router = Router(name="admin")

# Numeric settings that /set accepts. name -> (attr, min, max)
NUMERIC_SETTINGS = {
    "xp_per_message": ("xp_per_message", 1, 1000),
    "cooldown": ("xp_cooldown_sec", 0, 86400),
    "min_len": ("min_message_len", 0, 500),
    "antiflood": ("antiflood_window_sec", 0, 600),
}
TIME_SETTINGS = {"prompt_time": "daily_prompt_time", "weekly_time": "weekly_top_time"}
MODULES = {
    "welcome": "welcome_enabled",
    "xp": "xp_enabled",
    "leaderboard": "leaderboard_enabled",
    "daily": "daily_prompt_enabled",
}


async def is_admin(message: Message, bot: Bot, config: Config) -> bool:
    user = message.from_user
    if user is None:
        return False
    if user.id in config.admin_ids:
        return True
    if message.chat.type not in ("group", "supergroup"):
        return False
    try:
        member = await bot.get_chat_member(message.chat.id, user.id)
        return member.status in ("administrator", "creator")
    except Exception:  # pragma: no cover - network
        return False


def _valid_time(value: str) -> bool:
    try:
        hh, mm = value.split(":")
        return 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59
    except Exception:
        return False


@router.message(Command("settings"))
async def cmd_settings(message: Message, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    text = (
        "<b>Настройки чата / Chat settings</b>\n"
        f"lang: {c.lang}\n\n"
        f"welcome: {'on' if c.welcome_enabled else 'off'}\n"
        f"xp: {'on' if c.xp_enabled else 'off'}\n"
        f"leaderboard: {'on' if c.leaderboard_enabled else 'off'}\n"
        f"daily: {'on' if c.daily_prompt_enabled else 'off'}\n\n"
        f"xp_per_message: {c.xp_per_message}\n"
        f"cooldown: {c.xp_cooldown_sec} sec\n"
        f"min_len: {c.min_message_len}\n"
        f"antiflood: {c.antiflood_window_sec} sec\n"
        f"prompt_time: {c.daily_prompt_time}\n"
        f"weekly_time: {c.weekly_top_time} (dow={c.weekly_top_dow})\n\n"
        "Изменить: /set &lt;key&gt; &lt;value&gt; · /toggle &lt;module&gt;"
    )
    await message.answer(text)


@router.message(Command("set"))
async def cmd_set(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    args = (command.args or "").split()
    if len(args) < 2:
        await message.answer(t("settings_bad", c.lang))
        return
    key, value = args[0].lower(), args[1]

    if key in NUMERIC_SETTINGS:
        attr, lo, hi = NUMERIC_SETTINGS[key]
        try:
            num = int(value)
        except ValueError:
            await message.answer(t("settings_bad", c.lang))
            return
        if not (lo <= num <= hi):
            await message.answer(t("settings_bad", c.lang))
            return
        setattr(c, attr, num)
        await message.answer(t("settings_saved", c.lang))
        return

    if key in TIME_SETTINGS:
        if not _valid_time(value):
            await message.answer(t("settings_bad", c.lang))
            return
        setattr(c, TIME_SETTINGS[key], value)
        await message.answer(t("settings_saved", c.lang) + " (перезапустите бота для смены расписания)")
        return

    await message.answer(t("settings_bad", c.lang))


@router.message(Command("toggle"))
async def cmd_toggle(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    module = (command.args or "").strip().lower()
    if module not in MODULES:
        await message.answer(t("settings_bad", c.lang))
        return
    attr = MODULES[module]
    setattr(c, attr, not getattr(c, attr))
    state = "on" if getattr(c, attr) else "off"
    await message.answer(f"{module}: {state}")


@router.message(Command("setwelcome"))
async def cmd_setwelcome(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    text = (command.args or "").strip()
    if not text:
        await message.answer(t("settings_bad", c.lang))
        return
    if c.lang == "ru":
        c.welcome_text_ru = text
    else:
        c.welcome_text_en = text
    await message.answer(t("welcome_set", c.lang))


@router.message(Command("lang"))
async def cmd_lang(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    value = (command.args or "").strip().lower()
    if value not in ("ru", "en"):
        await message.answer(t("settings_bad", c.lang))
        return
    c.lang = value
    await message.answer(t("settings_saved", value))


@router.message(Command("prompt"))
async def cmd_prompt(message: Message, session: AsyncSession, bot: Bot, config: Config) -> None:
    if not await is_admin(message, bot, config):
        await message.answer(t("not_admin", "ru"))
        return
    c = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    view = await pick_prompt(session, c.id, c.lang)
    if view is None:
        await message.answer(t("settings_bad", c.lang))
        return
    if view.kind == "poll" and view.options:
        await message.answer_poll(question=view.text, options=view.options, is_anonymous=False)
    else:
        await message.answer(f"💬 {view.text}")
