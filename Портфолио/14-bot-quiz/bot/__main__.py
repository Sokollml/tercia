"""Application entry point: wire up the bot, database, scheduler and start polling.

Run with ``python -m bot``.
"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_settings
from .db import Database
from .handlers import register_handlers
from .logging_config import setup_logging
from .middlewares import ThrottlingMiddleware
from .scheduler import build_scheduler
from .seed import import_seed

logger = logging.getLogger(__name__)


async def _run() -> None:
    settings = load_settings()
    setup_logging(settings.log_level)

    if not settings.bot_token:
        raise SystemExit(
            "BOT_TOKEN is not set. Copy .env.example to .env and fill it in."
        )

    database = Database(settings.database_url)
    await database.create_all()

    added = await import_seed(database)
    if added:
        logger.info("Imported %d seed questions", added)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Dependencies injected into every handler via workflow data.
    dp["database"] = database
    dp["settings"] = settings

    dp.message.middleware(ThrottlingMiddleware(settings.rate_limit_seconds))
    register_handlers(dp)

    scheduler = build_scheduler(bot, database, settings)
    scheduler.start()

    logger.info("Bot starting (admins=%s, tz=%s)", settings.admin_ids, settings.tz)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # ``allowed_updates`` must include poll_answer so we receive votes.
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await database.dispose()


def main() -> None:
    try:
        asyncio.run(_run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down")


if __name__ == "__main__":
    main()
