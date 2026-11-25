"""Application bootstrap: wire config, DB, dispatcher, scheduler and poll."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import Config, load_config
from .db import get_database
from .dbsetup import apply_schema
from .handlers import build_router
from .logger import setup_logging
from .middlewares import ThrottlingMiddleware
from .moderation import FloodTracker
from .repository import Repository
from .scheduler import setup_scheduler


async def run(cfg: Config) -> None:
    log = logging.getLogger("moderation")

    if not cfg.bot_token:
        raise RuntimeError("BOT_TOKEN is not set (see .env.example)")

    db = get_database(cfg)
    await db.connect()
    await apply_schema(db)
    log.info("database ready (driver=%s)", db.driver)

    repo = Repository(db, cfg)
    bot = Bot(cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    # Shared dependencies injected into every handler by keyword.
    dp["repo"] = repo
    dp["flood"] = FloodTracker(cfg.antiflood_limit, cfg.antiflood_window)

    throttle = ThrottlingMiddleware(cfg.rate_limit, cfg.rate_window)
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)

    dp.include_router(build_router())

    scheduler = setup_scheduler(bot, repo, cfg)
    scheduler.start()
    log.info("scheduler started")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        allowed = dp.resolve_used_update_types()
        log.info("start polling (updates=%s)", allowed)
        await dp.start_polling(bot, allowed_updates=allowed)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await db.close()
        log.info("shutdown complete")


def main() -> None:
    cfg = load_config()
    setup_logging(cfg.log_level)
    try:
        asyncio.run(run(cfg))
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        logging.getLogger("moderation").info("interrupted, exiting")


if __name__ == "__main__":  # pragma: no cover
    main()
