"""Spaced-repetition reminders via APScheduler.

Once a day (configurable) we scan for users who have mistakes due for review and
nudge them with a short message.  The scan query is kept in the repository; this
module only wires it to a scheduled job and the bot's ``send_message``.

The APScheduler import is lazy so the module stays import-safe in tests.
Compatible with Python 3.9.
"""
from __future__ import annotations

import logging
from typing import Any, List

from . import services
from .config import Config
from .i18n import t
from .repository import Repository

log = logging.getLogger("tutor.scheduler")

# Only remind users with at least this many due items, to avoid noise.
MIN_DUE_FOR_REMINDER = 1


async def find_users_to_remind(repo: Repository, now_ts: int) -> List[dict]:
    """Return onboarded users who currently have due review items."""
    rows = await repo.db.fetchall(
        "SELECT u.id AS user_id, u.ui_lang AS ui_lang, COUNT(m.id) AS due "
        "FROM users u JOIN mistakes m ON m.user_id = u.id "
        "WHERE u.learn_lang IS NOT NULL AND m.next_review <= ? "
        "GROUP BY u.id, u.ui_lang "
        "HAVING COUNT(m.id) >= ?",
        now_ts,
        MIN_DUE_FOR_REMINDER,
    )
    return rows


async def send_due_reminders(bot: Any, repo: Repository) -> int:
    """Send one reminder per eligible user; return how many were sent."""
    sent = 0
    users = await find_users_to_remind(repo, services.now_ts())
    for row in users:
        ui_lang = row.get("ui_lang", "ru")
        text = t("reminder", ui_lang, n=int(row.get("due") or 0))
        try:
            await bot.send_message(int(row["user_id"]), text)
            sent += 1
        except Exception as exc:  # user blocked bot, etc. — keep going
            log.warning("reminder to %s failed: %s", row.get("user_id"), exc)
    log.info("sent %s spaced-repetition reminders", sent)
    return sent


def build_scheduler(bot: Any, repo: Repository, cfg: Config):
    """Create and return a configured (not yet started) AsyncIOScheduler."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler(timezone=cfg.tz)
    # Daily nudge at 10:00 local time.
    scheduler.add_job(
        send_due_reminders,
        trigger=CronTrigger(hour=10, minute=0, timezone=cfg.tz),
        args=[bot, repo],
        id="due_reminders",
        replace_existing=True,
    )
    return scheduler
