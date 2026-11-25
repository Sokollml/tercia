"""APScheduler wiring: auto-finish giveaways when their time is up."""

from __future__ import annotations

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .db import Database
from .services import run_draw

log = logging.getLogger(__name__)


async def _tick(bot: Bot, db: Database) -> None:
    """Find due giveaways and run their draws."""
    try:
        due = await db.due_giveaways()
    except Exception as exc:  # pragma: no cover - defensive
        log.error("scheduler tick failed to query due giveaways: %s", exc)
        return
    for giveaway in due:
        try:
            await run_draw(bot, db, giveaway)
        except Exception as exc:  # pragma: no cover - defensive
            log.exception("draw failed for giveaway %s: %s", giveaway.get("id"), exc)


def setup_scheduler(bot: Bot, db: Database, tz: str = "UTC") -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        _tick, "interval", seconds=30, args=[bot, db], id="auto_finish",
        replace_existing=True, max_instances=1,
    )
    return scheduler
