"""Admin settings: /settings (view) and /set <key> <value> (edit)."""
from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from .. import i18n
from ..repository import ALLOWED_SETTINGS, Repository
from ..utils import is_user_admin

log = logging.getLogger("moderation.handlers.settings")
router = Router(name="settings")

# Type coercion per editable column.
_BOOL_KEYS = {
    "captcha_enabled",
    "filter_links",
    "filter_forwards",
    "filter_stopwords",
    "antiflood_enabled",
}
_INT_KEYS = {
    "captcha_timeout",
    "antiflood_limit",
    "antiflood_window",
    "warn_limit",
    "mute_duration",
}
_TEXT_KEYS = {"lang", "stopwords", "rules_text", "welcome_text"}

# Keys surfaced in the /settings overview (texts are edited via dedicated cmds).
_OVERVIEW_KEYS = [
    "lang",
    "captcha_enabled",
    "captcha_timeout",
    "filter_links",
    "filter_forwards",
    "filter_stopwords",
    "stopwords",
    "antiflood_enabled",
    "antiflood_limit",
    "antiflood_window",
    "warn_limit",
    "mute_duration",
]

_TRUE = {"1", "true", "on", "yes", "да", "вкл"}
_FALSE = {"0", "false", "off", "no", "нет", "выкл"}


def _coerce(key: str, raw: str) -> Any:
    raw = raw.strip()
    if key in _BOOL_KEYS:
        low = raw.lower()
        if low in _TRUE:
            return 1
        if low in _FALSE:
            return 0
        raise ValueError("expected on/off")
    if key in _INT_KEYS:
        return int(raw)  # raises ValueError on bad input
    if key == "lang":
        low = raw.lower()
        if low not in ("ru", "en"):
            raise ValueError("expected ru/en")
        return low
    return raw  # free text


@router.message(Command("settings"))
async def cmd_settings(message: Message, bot: Bot, repo: Repository) -> None:
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return
    lines = [i18n.t(lang, "settings_header", title=message.chat.title or message.chat.id)]
    for key in _OVERVIEW_KEYS:
        lines.append("• %s = %s" % (key, row.get(key)))
    await message.answer("\n".join(lines))


@router.message(Command("set"))
async def cmd_set(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return

    args = (command.args or "").strip()
    if not args or " " not in args:
        await message.answer(i18n.t(lang, "usage_set"))
        return
    key, _, value = args.partition(" ")
    key = key.strip().lower()
    if key not in ALLOWED_SETTINGS:
        editable = ", ".join(sorted(_BOOL_KEYS | _INT_KEYS | _TEXT_KEYS))
        await message.answer(i18n.t(lang, "unknown_setting", keys=editable))
        return
    try:
        coerced = _coerce(key, value)
    except ValueError:
        await message.answer(i18n.t(lang, "usage_set"))
        return
    await repo.update_setting(message.chat.id, key, coerced)
    await repo.log_action(
        message.chat.id, "setting_change", actor_id=message.from_user.id, details="%s=%s" % (key, coerced)
    )
    await message.answer(i18n.t(lang, "setting_updated", key=key, value=coerced))
