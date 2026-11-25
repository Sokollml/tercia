"""Admin commands: run quizzes, manage the question bank and seasons.

Every handler here is guarded by :class:`IsAdmin` (bot admins are configured via
``ADMIN_IDS``). The ``/addquestion`` wizard uses a small FSM so admins can add a
question interactively without learning a command syntax.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from .. import db as repo
from ..config import Settings
from ..i18n import SUPPORTED, normalize_lang, t
from ..quiz_service import format_leaderboard, format_winners, run_series, run_single
from .utils import resolve_lang

logger = logging.getLogger(__name__)
router = Router(name="admin")


class IsAdmin:
    """Filter that passes only for configured bot admins."""

    async def __call__(self, message: Message, settings: Settings) -> bool:
        return bool(message.from_user and settings.is_admin(message.from_user.id))


# Apply the admin guard to every message handler in this router.
router.message.filter(IsAdmin())


def _group_only(message: Message) -> bool:
    return message.chat.type in {"group", "supergroup"}


# --------------------------------------------------------------------------- #
# Running quizzes
# --------------------------------------------------------------------------- #
@router.message(Command("quiz"))
async def cmd_quiz(
    message: Message,
    command: CommandObject,
    bot: Bot,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    if not _group_only(message):
        await message.answer(t("group_only", lang))
        return
    category = (command.args or "").strip() or None
    async with database.session() as session:
        await repo.ensure_chat(session, message.chat.id, settings.default_lang)
    await run_single(
        bot, database, settings,
        chat_id=message.chat.id, category=category, mode="daily",
    )


@router.message(Command("marathon"))
async def cmd_marathon(
    message: Message,
    command: CommandObject,
    bot: Bot,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    if not _group_only(message):
        await message.answer(t("group_only", lang))
        return
    category = (command.args or "").strip() or None
    async with database.session() as session:
        await repo.ensure_chat(session, message.chat.id, settings.default_lang)
    await run_series(
        bot, database, settings,
        chat_id=message.chat.id, mode="marathon",
        size=settings.marathon_size, gap_seconds=settings.marathon_gap_seconds,
        open_period=settings.poll_open_seconds, category=category,
    )


@router.message(Command("blitz"))
async def cmd_blitz(
    message: Message,
    command: CommandObject,
    bot: Bot,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    if not _group_only(message):
        await message.answer(t("group_only", lang))
        return
    category = (command.args or "").strip() or None
    async with database.session() as session:
        await repo.ensure_chat(session, message.chat.id, settings.default_lang)
    await run_series(
        bot, database, settings,
        chat_id=message.chat.id, mode="blitz",
        size=settings.blitz_size, gap_seconds=settings.blitz_gap_seconds,
        open_period=settings.blitz_gap_seconds, category=category,
    )


# --------------------------------------------------------------------------- #
# Daily schedule subscription
# --------------------------------------------------------------------------- #
@router.message(Command("daily"))
async def cmd_daily(
    message: Message,
    command: CommandObject,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    arg = (command.args or "").strip().lower()
    if arg not in {"on", "off"}:
        await message.answer(t("daily_usage", lang))
        return
    async with database.session() as session:
        await repo.set_daily(session, message.chat.id, arg == "on")
    await message.answer(t("daily_on" if arg == "on" else "daily_off", lang))


# --------------------------------------------------------------------------- #
# Seasons
# --------------------------------------------------------------------------- #
@router.message(Command("newseason"))
async def cmd_newseason(
    message: Message,
    command: CommandObject,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    title = (command.args or "").strip()
    if not title:
        await message.answer(t("newseason_usage", lang))
        return
    async with database.session() as session:
        season = await repo.start_new_season(session, title)
    await message.answer(t("season_started", lang, season=season.title))


@router.message(Command("endseason"))
async def cmd_endseason(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    async with database.session() as session:
        season = await repo.get_active_season(session)
        if season is None:
            await message.answer(t("no_active_season", lang))
            return
        scores = await repo.get_leaderboard(session, season.id, limit=3)
        await repo.end_season(session, season)

    text = t("season_ended", lang, season=season.title) + "\n\n" + format_winners(
        scores, lang
    )
    await message.answer(text)


@router.message(Command("results"))
async def cmd_results(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    async with database.session() as session:
        season = await repo.get_active_season(session)
        if season is None:
            await message.answer(t("no_active_season", lang))
            return
        scores = await repo.get_leaderboard(session, season.id, limit=10)
    # Reuse the leaderboard formatter but with a "current results" header line.
    body = format_leaderboard(scores, season.title, lang)
    await message.answer(t("results_title", lang, season=season.title) + "\n" + body)


@router.message(Command("categories"))
async def cmd_categories(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    async with database.session() as session:
        cats = await repo.list_categories(session)
    if not cats:
        await message.answer(t("no_questions", lang))
        return
    await message.answer(t("categories_title", lang) + "\n" + "\n".join(f"• {c}" for c in cats))


# --------------------------------------------------------------------------- #
# /addquestion wizard (FSM)
# --------------------------------------------------------------------------- #
class AddQuestion(StatesGroup):
    category = State()
    lang = State()
    text = State()
    options = State()


def _parse_options(raw: str) -> Optional[Dict[str, Any]]:
    """Parse the multi-line options block.

    One option per line; the correct one is prefixed with ``*``. Returns a dict
    ``{"options": [...], "correct_index": int}`` or ``None`` if invalid.
    """
    options: List[str] = []
    correct_index: Optional[int] = None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("*"):
            if correct_index is not None:
                return None  # more than one correct option
            correct_index = len(options)
            line = line[1:].strip()
        if not line:
            continue
        options.append(line[:100])
    if correct_index is None or not (2 <= len(options) <= 10):
        return None
    return {"options": options, "correct_index": correct_index}


@router.message(Command("cancel"))
async def cmd_cancel(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer(t("aq_cancelled", lang))


@router.message(Command("addquestion"))
async def cmd_addquestion(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    await state.set_state(AddQuestion.category)
    await message.answer(t("aq_category", lang))


@router.message(AddQuestion.category)
async def aq_category(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    await state.update_data(category=(message.text or "").strip()[:100])
    await state.set_state(AddQuestion.lang)
    await message.answer(t("aq_lang", lang))


@router.message(AddQuestion.lang)
async def aq_lang(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    ui_lang = await resolve_lang(
        database, settings, message.chat.id, message.from_user
    )
    q_lang = normalize_lang((message.text or "").strip().lower())
    if q_lang not in SUPPORTED:
        q_lang = settings.default_lang
    await state.update_data(lang=q_lang)
    await state.set_state(AddQuestion.text)
    await message.answer(t("aq_text", ui_lang))


@router.message(AddQuestion.text)
async def aq_text(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    await state.update_data(text=(message.text or "").strip()[:300])
    await state.set_state(AddQuestion.options)
    await message.answer(t("aq_options", lang))


@router.message(AddQuestion.options)
async def aq_options(
    message: Message,
    state: FSMContext,
    database: repo.Database,
    settings: Settings,
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    parsed = _parse_options(message.text or "")
    if parsed is None:
        await message.answer(t("aq_bad_options", lang))
        return

    data = await state.get_data()
    await state.clear()
    async with database.session() as session:
        question = await repo.add_question(
            session,
            category=data.get("category", "General"),
            lang=data.get("lang", settings.default_lang),
            text=data.get("text", ""),
            options=parsed["options"],
            correct_index=parsed["correct_index"],
        )
    await message.answer(
        t("aq_saved", lang, id=question.id, category=question.category)
    )
