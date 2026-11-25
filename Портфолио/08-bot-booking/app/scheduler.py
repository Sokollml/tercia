"""Reminder scheduler built on APScheduler.

Every minute it polls the repository for confirmed bookings whose one-hour
reminder is due and sends them, marking each as reminded to avoid duplicates.
"""
from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .repository import Repository
from .services import format_when, now_ts
from .texts import t

log = logging.getLogger("booking.scheduler")

POLL_SECONDS = 60


class ReminderScheduler:
    def __init__(self, bot, repo: Repository, tz: str, lang_store) -> None:
        self.bot = bot
        self.repo = repo
        self.tz = tz
        self.lang_store = lang_store
        self._scheduler: Optional[AsyncIOScheduler] = None

    def start(self) -> None:
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._scheduler.add_job(
            self._tick,
            "interval",
            seconds=POLL_SECONDS,
            id="reminder_poll",
            replace_existing=True,
            next_run_time=None,
        )
        self._scheduler.start()
        log.info("Reminder scheduler started (poll every %ss)", POLL_SECONDS)

    def shutdown(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None

    async def _tick(self) -> None:
        """Send any reminders whose fire time has arrived."""
        try:
            current = now_ts()
            due = await self.repo.due_reminders(now_ts=current, horizon_ts=current)
            for row in due:
                await self._send_one(row)
        except Exception:  # pragma: no cover - defensive; keep scheduler alive
            log.exception("reminder tick failed")

    async def _send_one(self, row) -> None:
        client_id = row["client_id"]
        lang = self.lang_store.get(client_id, "ru")
        text = t(
            "reminder",
            lang,
            service=row["service_title"],
            when=format_when(row["start_ts"], self.tz),
        )
        try:
            await self.bot.send_message(client_id, text)
            await self.repo.mark_reminder_sent(row["id"])
            log.info("reminder sent for booking %s", row["id"])
        except Exception:  # pragma: no cover - client may have blocked the bot
            log.exception("failed to send reminder for booking %s", row["id"])
            # Mark as sent anyway to avoid endless retries on a dead chat.
            await self.repo.mark_reminder_sent(row["id"])
