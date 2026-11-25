"""High-level quiz orchestration: publish native Telegram quiz polls and run
daily / marathon / blitz rounds. Kept separate from handlers so it can be
driven both by admin commands and by the scheduler.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter

from . import db as repo
from .config import Settings
from .i18n import t
from .models import Question

logger = logging.getLogger(__name__)


async def _safe_send_poll(bot: Bot, **kwargs):
    """Send a poll, transparently honouring Telegram flood-control waits."""
    try:
        return await bot.send_poll(**kwargs)
    except TelegramRetryAfter as exc:  # pragma: no cover - network path
        logger.warning("Flood control: sleeping %ss before retry", exc.retry_after)
        await asyncio.sleep(exc.retry_after + 1)
        return await bot.send_poll(**kwargs)


async def publish_question(
    bot: Bot,
    database: repo.Database,
    settings: Settings,
    *,
    chat_id: int,
    question: Question,
    mode: str,
    season_id: Optional[int],
    open_period: Optional[int] = None,
) -> Optional[str]:
    """Publish one question as a native quiz poll and register it.

    Returns the Telegram ``poll_id`` on success, or ``None`` on failure.
    """
    open_period = open_period or settings.poll_open_seconds
    # Telegram requires 5..600 seconds for a poll open_period.
    open_period = max(5, min(600, open_period))

    try:
        message = await _safe_send_poll(
            bot,
            chat_id=chat_id,
            question=question.text[:300],
            options=[str(o)[:100] for o in question.options],
            type="quiz",
            correct_option_id=question.correct_index,
            explanation=(question.explanation or None),
            is_anonymous=False,
            open_period=open_period,
        )
    except Exception:  # pragma: no cover - network path
        logger.exception("Failed to send poll to chat %s", chat_id)
        return None

    poll_id = message.poll.id
    closes_at = datetime.utcnow() + timedelta(seconds=open_period)
    async with database.session() as session:
        await repo.create_quiz(
            session,
            poll_id=poll_id,
            chat_id=chat_id,
            message_id=message.message_id,
            question_id=question.id,
            season_id=season_id,
            mode=mode,
            correct_index=question.correct_index,
            closes_at=closes_at,
        )
    logger.info("Published %s question id=%s poll=%s to chat=%s", mode, question.id, poll_id, chat_id)
    return poll_id


async def _resolve_context(
    database: repo.Database, chat_id: int, settings: Settings
):
    """Return (lang, active_season_id) for a chat."""
    async with database.session() as session:
        lang = await repo.get_chat_lang(session, chat_id, settings.default_lang)
        season = await repo.get_active_season(session)
    return lang, (season.id if season else None)


async def run_single(
    bot: Bot,
    database: repo.Database,
    settings: Settings,
    *,
    chat_id: int,
    category: Optional[str] = None,
    mode: str = "daily",
) -> bool:
    """Publish a single question. Returns True if a question was published."""
    lang, season_id = await _resolve_context(database, chat_id, settings)
    async with database.session() as session:
        questions = await repo.pick_questions(
            session, lang=lang, category=category, limit=1
        )
    if not questions:
        await bot.send_message(chat_id, t("no_questions", lang))
        return False

    if mode == "daily":
        await bot.send_message(
            chat_id, t("quiz_intro", lang, category=questions[0].category)
        )
    await publish_question(
        bot, database, settings,
        chat_id=chat_id, question=questions[0], mode=mode, season_id=season_id,
    )
    return True


async def run_series(
    bot: Bot,
    database: repo.Database,
    settings: Settings,
    *,
    chat_id: int,
    mode: str,
    size: int,
    gap_seconds: int,
    open_period: int,
    category: Optional[str] = None,
) -> int:
    """Run a series of questions (marathon / blitz). Returns number published."""
    lang, season_id = await _resolve_context(database, chat_id, settings)
    async with database.session() as session:
        questions = await repo.pick_questions(
            session, lang=lang, category=category, limit=size
        )
    if not questions:
        await bot.send_message(chat_id, t("no_questions", lang))
        return 0

    intro_key = "marathon_intro" if mode == "marathon" else "blitz_intro"
    await bot.send_message(chat_id, t(intro_key, lang, n=len(questions)))

    published = 0
    for idx, question in enumerate(questions):
        ok = await publish_question(
            bot, database, settings,
            chat_id=chat_id, question=question, mode=mode, season_id=season_id,
            open_period=open_period,
        )
        if ok:
            published += 1
        # Do not sleep after the last question.
        if idx < len(questions) - 1:
            await asyncio.sleep(gap_seconds)
    return published


def format_leaderboard(scores, season_title: str, lang: str) -> str:
    if not scores:
        return t("leaderboard_title", lang, season=season_title) + "\n" + t(
            "leaderboard_empty", lang
        )
    medals = ["🥇", "🥈", "🥉"]
    lines = [t("leaderboard_title", lang, season=season_title)]
    for i, s in enumerate(scores):
        prefix = medals[i] if i < len(medals) else f"{i + 1}."
        name = s.username or f"id{s.user_id}"
        lines.append(f"{prefix} {name} — {s.points} ({s.correct_count}/{s.total_count})")
    return "\n".join(lines)


def format_winners(scores: List, lang: str) -> str:
    if not scores:
        return t("leaderboard_empty", lang)
    medals = ["🥇", "🥈", "🥉"]
    lines = [t("winners", lang)]
    for i, s in enumerate(scores[:3]):
        name = s.username or f"id{s.user_id}"
        lines.append(f"{medals[i]} {name} — {s.points}")
    return "\n".join(lines)
