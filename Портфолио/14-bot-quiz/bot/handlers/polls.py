"""Handle native Telegram quiz-poll answers and award points.

This is the heart of the bot: every :class:`aiogram.types.PollAnswer` is mapped
back to the quiz we published, checked for correctness, scored (with an optional
speed bonus) and stored exactly once per user via the unique
``(poll_id, user_id)`` constraint enforced in :func:`bot.db.record_answer`.
"""
from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import PollAnswer

from .. import db as repo
from ..config import Settings
from ..scoring import calculate_points
from .utils import display_name

logger = logging.getLogger(__name__)
router = Router(name="polls")


@router.poll_answer()
async def on_poll_answer(
    poll_answer: PollAnswer, database: repo.Database, settings: Settings
) -> None:
    # A retracted vote (empty option_ids) carries no answer to score.
    if not poll_answer.option_ids:
        return

    option_index = poll_answer.option_ids[0]
    user = poll_answer.user
    user_id = user.id if user else 0

    async with database.session() as session:
        quiz = await repo.get_quiz_by_poll(session, poll_answer.poll_id)
        if quiz is None:
            logger.debug("Poll answer for unknown poll_id=%s", poll_answer.poll_id)
            return

        is_correct = option_index == quiz.correct_index

        elapsed = None
        if quiz.opened_at is not None:
            elapsed = (datetime.utcnow() - quiz.opened_at).total_seconds()

        points = calculate_points(
            is_correct,
            base_points=settings.base_points,
            elapsed_seconds=elapsed,
            speed_window_seconds=settings.speed_window_seconds,
            speed_bonus_max=settings.speed_bonus_max,
        )

        stored = await repo.record_answer(
            session,
            quiz=quiz,
            user_id=user_id,
            username=display_name(user),
            option_index=option_index,
            is_correct=is_correct,
            points=points,
        )

    if stored:
        logger.info(
            "Scored user=%s poll=%s correct=%s points=%s",
            user_id,
            poll_answer.poll_id,
            is_correct,
            points,
        )
    else:
        logger.debug(
            "Duplicate answer ignored user=%s poll=%s", user_id, poll_answer.poll_id
        )
