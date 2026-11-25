"""APScheduler jobs: daily prompt + weekly leaderboard post."""
from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.db import Chat
from bot.i18n import t
from bot.services.leaderboard import weekly_top
from bot.services.prompts import pick_prompt

log = logging.getLogger(__name__)


def _medal(pos: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, f"{pos}.")


async def send_daily_prompt(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
        chats = (
            await session.execute(select(Chat).where(Chat.daily_prompt_enabled.is_(True)))
        ).scalars().all()
        for chat in chats:
            view = await pick_prompt(session, chat.id, chat.lang)
            if view is None:
                continue
            try:
                if view.kind == "poll" and view.options:
                    await bot.send_poll(chat.id, question=view.text, options=view.options, is_anonymous=False)
                else:
                    await bot.send_message(chat.id, f"💬 {view.text}")
            except Exception as exc:  # pragma: no cover - network
                log.warning("daily prompt to %s failed: %s", chat.id, exc)


async def post_weekly_top(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> None:
    now = datetime.utcnow()
    async with session_factory() as session:
        chats = (
            await session.execute(select(Chat).where(Chat.leaderboard_enabled.is_(True)))
        ).scalars().all()
        for chat in chats:
            rows = await weekly_top(session, chat.id, now=now, limit=10)
            if not rows:
                continue
            lines = [t("top_header_week", chat.lang)]
            lines += [f"{_medal(r.position)} {r.name} — {r.value} XP" for r in rows]
            lines.append("")
            lines.append(t("weekly_congrats", chat.lang))
            try:
                await bot.send_message(chat.id, "\n".join(lines))
            except Exception as exc:  # pragma: no cover - network
                log.warning("weekly top to %s failed: %s", chat.id, exc)


def build_scheduler(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    tz: str,
    daily_time: str = "10:00",
    weekly_dow: int = 0,
    weekly_time: str = "12:00",
) -> AsyncIOScheduler:
    """Global schedule. Per-chat time overrides are stored in DB; here we use
    sensible global defaults from .env to keep the scheduler simple."""
    scheduler = AsyncIOScheduler(timezone=tz)

    dh, dm = [int(x) for x in daily_time.split(":")]
    scheduler.add_job(
        send_daily_prompt,
        CronTrigger(hour=dh, minute=dm, timezone=tz),
        args=[bot, session_factory],
        id="daily_prompt",
        replace_existing=True,
    )

    wh, wm = [int(x) for x in weekly_time.split(":")]
    scheduler.add_job(
        post_weekly_top,
        CronTrigger(day_of_week=weekly_dow, hour=wh, minute=wm, timezone=tz),
        args=[bot, session_factory],
        id="weekly_top",
        replace_existing=True,
    )
    return scheduler
