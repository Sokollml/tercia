"""APScheduler integration: post the scheduled daily question.

A single cron job runs once a day (``DAILY_CRON_HOUR``/``DAILY_CRON_MINUTE`` in
the configured ``TZ``) and publishes one question to every chat that opted in
with ``/daily on``.
"""
from __future__ import annotations

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import db as repo
from .config import Settings
from .quiz_service import run_single

logger = logging.getLogger(__name__)


async def post_daily_questions(
    bot: Bot, database: repo.Database, settings: Settings
) -> None:
    """Publish the daily question to every subscribed chat."""
    async with database.session() as session:
        chat_ids = await repo.get_daily_chats(session)
    if not chat_ids:
        logger.info("Daily job: no subscribed chats")
        return
    logger.info("Daily job: posting to %d chat(s)", len(chat_ids))
    for chat_id in chat_ids:
        try:
            await run_single(
                bot, database, settings, chat_id=chat_id, mode="daily"
            )
        except Exception:  # pragma: no cover - network path, keep going
            logger.exception("Daily job failed for chat %s", chat_id)


def build_scheduler(
    bot: Bot, database: repo.Database, settings: Settings
) -> AsyncIOScheduler:
    """Create (but do not start) the scheduler with the daily cron job."""
    scheduler = AsyncIOScheduler(timezone=settings.tz)
    scheduler.add_job(
        post_daily_questions,
        trigger=CronTrigger(
            hour=settings.daily_cron_hour,
            minute=settings.daily_cron_minute,
            timezone=settings.tz,
        ),
        kwargs={"bot": bot, "database": database, "settings": settings},
        id="daily_question",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    return scheduler
