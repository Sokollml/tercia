"""Shared helpers and universal commands (/help, /cancel).

Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import services
from ..config import LEARN_LANGUAGES
from ..i18n import normalise_ui_lang, t
from ..repository import Repository

router = Router(name="common")


async def get_user_ctx(message: Message, repo: Repository) -> Dict[str, Any]:
    """Fetch (creating if needed) the user row and normalise its UI language."""
    user = await repo.ensure_user(
        message.from_user.id,
        normalise_ui_lang(message.from_user.language_code or "ru"),
        services.now_ts(),
    )
    return user


def is_onboarded(user: Optional[Dict[str, Any]]) -> bool:
    return bool(user and user.get("learn_lang") and user.get("level"))


def learn_lang_name(code: Optional[str], ui_lang: str) -> str:
    entry = LEARN_LANGUAGES.get(code or "", None)
    if entry is None:
        return code or "?"
    return entry.get(ui_lang, entry["en"])


@router.message(Command("help"))
async def cmd_help(message: Message, repo: Repository, **_: Any) -> None:
    user = await get_user_ctx(message, repo)
    await message.answer(t("help", user.get("ui_lang", "ru")))


@router.message(Command("cancel"))
async def cmd_cancel(
    message: Message, state: FSMContext, repo: Repository, **_: Any
) -> None:
    user = await get_user_ctx(message, repo)
    ui_lang = user.get("ui_lang", "ru")
    current = await state.get_state()
    if current is None:
        await message.answer(t("nothing_to_cancel", ui_lang))
        return
    await state.clear()
    await message.answer(t("cancelled", ui_lang))
