"""Player-facing commands: /leaderboard, /myscore."""
from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .. import db as repo
from ..config import Settings
from ..i18n import t
from ..quiz_service import format_leaderboard
from .utils import resolve_lang

logger = logging.getLogger(__name__)
router = Router(name="player")


@router.message(Command("leaderboard", "top"))
async def cmd_leaderboard(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    async with database.session() as session:
        season = await repo.get_active_season(session)
        if season is None:
            await message.answer(t("no_active_season", lang))
            return
        scores = await repo.get_leaderboard(session, season.id, limit=10)
    await message.answer(format_leaderboard(scores, season.title, lang))


@router.message(Command("myscore", "me"))
async def cmd_myscore(
    message: Message, database: repo.Database, settings: Settings
) -> None:
    lang = await resolve_lang(database, settings, message.chat.id, message.from_user)
    if message.from_user is None:
        return
    async with database.session() as session:
        season = await repo.get_active_season(session)
        if season is None:
            await message.answer(t("no_active_season", lang))
            return
        score = await repo.get_user_score(session, season.id, message.from_user.id)
    if score is None:
        await message.answer(t("myscore_none", lang))
        return
    await message.answer(
        t(
            "myscore",
            lang,
            season=season.title,
            points=score.points,
            correct=score.correct_count,
            total=score.total_count,
        )
    )
