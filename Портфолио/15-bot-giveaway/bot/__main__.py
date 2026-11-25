"""Application entry point.

Run with::

    python -m bot

Wires together configuration, the database layer, the aiogram dispatcher
(with rate-limiting middleware and injected dependencies) and the
APScheduler job that auto-finishes giveaways when their time is up.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import Config, load_config
from .db import Database
from .handlers import build_router
from .middlewares import ThrottlingMiddleware
from .scheduler import setup_scheduler

log = logging.getLogger("bot")


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


async def _run(config: Config) -> None:
    if not config.bot_token:
        raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    db = Database(config.db_engine, config.db_dsn)
    await db.connect()
    log.info("database ready (engine=%s)", config.db_engine)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    # Dependencies injected into every handler that declares them.
    dp["db"] = db
    dp["config"] = config

    throttle = ThrottlingMiddleware(rate=config.rate_limit_seconds)
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)

    dp.include_router(build_router())

    scheduler = setup_scheduler(bot, db, tz=config.tz)
    scheduler.start()
    log.info("scheduler started")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("starting polling")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await db.close()
        log.info("shutdown complete")


def main() -> None:
    config = load_config()
    _setup_logging(config.log_level)
    try:
        asyncio.run(_run(config))
    except (KeyboardInterrupt, SystemExit) as exc:
        if isinstance(exc, SystemExit) and exc.code:
            log.error("%s", exc)
            sys.exit(exc.code)
        log.info("interrupted, exiting")


if __name__ == "__main__":
    main()
