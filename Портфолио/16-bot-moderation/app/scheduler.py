"""APScheduler wiring — captcha timeout enforcement.

A single periodic job scans the ``captcha_pending`` table and kicks newcomers
whose deadline has passed. Persisting pending challenges in the DB (rather than
scheduling one job per user) means restarts don't lose in-flight captchas.
"""
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import utils
from .config import Config
from .moderation import now_ts
from .repository import Repository

log = logging.getLogger("moderation.scheduler")

# How often to look for expired captchas.
SCAN_INTERVAL_SECONDS = 5


async def enforce_captcha_timeouts(bot: Bot, repo: Repository, now: Optional[int] = None) -> int:
    """Kick every newcomer whose captcha deadline has passed.

    Returns the number of users kicked (handy for tests / metrics).
    """
    current = now_ts() if now is None else now
    due = await repo.due_pending(current)
    kicked = 0
    for row in due:
        chat_id = int(row["chat_id"])
        user_id = int(row["user_id"])
        # Remove the pending record first so a slow kick can't double-fire.
        await repo.remove_pending(chat_id, user_id)
        message_id = int(row.get("message_id") or 0)
        if message_id:
            await utils.delete_message_safe(bot, chat_id, message_id)
        ok = await utils.kick_user(bot, chat_id, user_id)
        await repo.log_action(
            chat_id, "captcha_timeout_kick", actor_id=0, target_id=user_id
        )
        if ok:
            kicked += 1
        log.info("captcha timeout: user=%s chat=%s kicked=%s", user_id, chat_id, ok)
    return kicked


def setup_scheduler(bot: Bot, repo: Repository, cfg: Config) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=cfg.tz)
    scheduler.add_job(
        enforce_captcha_timeouts,
        trigger="interval",
        seconds=SCAN_INTERVAL_SECONDS,
        args=[bot, repo],
        id="captcha_timeouts",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    return scheduler
