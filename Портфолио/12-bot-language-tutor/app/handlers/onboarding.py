"""Onboarding flow: /start → UI language → target language → CEFR level.

Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import keyboards
from ..i18n import normalise_ui_lang, t
from ..repository import Repository
from ..states import Dialog, Onboarding
from .common import get_user_ctx, learn_lang_name

router = Router(name="onboarding")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, repo: Repository, **_: Any) -> None:
    user = await get_user_ctx(message, repo)
    await state.clear()
    await state.set_state(Onboarding.ui_lang)
    await message.answer(
        t("start", user.get("ui_lang", "ru")),
        reply_markup=keyboards.ui_lang_keyboard(),
    )


@router.callback_query(F.data.startswith(keyboards.CB_UI_LANG + ":"))
async def on_ui_lang(cq: CallbackQuery, state: FSMContext, repo: Repository, **_: Any) -> None:
    _, values = keyboards.parse_callback(cq.data)
    ui_lang = normalise_ui_lang(values[0] if values else "ru")
    await repo.set_ui_lang(cq.from_user.id, ui_lang)
    await state.set_state(Onboarding.learn_lang)
    await cq.message.edit_text(
        t("choose_learn_lang", ui_lang),
        reply_markup=keyboards.learn_lang_keyboard(ui_lang),
    )
    await cq.answer()


@router.callback_query(F.data.startswith(keyboards.CB_LEARN_LANG + ":"))
async def on_learn_lang(cq: CallbackQuery, state: FSMContext, repo: Repository, **_: Any) -> None:
    _, values = keyboards.parse_callback(cq.data)
    learn_lang = values[0] if values else "en"
    user = await repo.get_user(cq.from_user.id)
    ui_lang = (user or {}).get("ui_lang", "ru")
    await repo.set_learn_lang(cq.from_user.id, learn_lang)
    await state.set_state(Onboarding.level)
    await cq.message.edit_text(
        t("choose_level", ui_lang, lang=learn_lang_name(learn_lang, ui_lang)),
        reply_markup=keyboards.level_keyboard(),
    )
    await cq.answer()


@router.callback_query(F.data.startswith(keyboards.CB_LEVEL + ":"))
async def on_level(cq: CallbackQuery, state: FSMContext, repo: Repository, **_: Any) -> None:
    _, values = keyboards.parse_callback(cq.data)
    level = values[0] if values else "A1"
    await repo.set_level(cq.from_user.id, level)
    user = await repo.get_user(cq.from_user.id)
    ui_lang = (user or {}).get("ui_lang", "ru")
    lang = learn_lang_name((user or {}).get("learn_lang"), ui_lang)
    await state.set_state(Dialog.chatting)
    await cq.message.edit_text(
        t("onboarding_done", ui_lang, lang=lang, level=level)
    )
    await cq.answer()
