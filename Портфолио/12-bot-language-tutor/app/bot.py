"""Application bootstrap: build the bot, wire dependencies, run polling.

Kept separate from the pure modules so importing ``app.bot`` is the only place
that requires aiogram/APScheduler at runtime.  Compatible with Python 3.9.
"""
from __future__ import annotations

import asyncio
import logging
import os

from .config import Config, load_config
from .db import Database, get_database
from .llm import LLMClient
from .logger import setup_logging
from .repository import Repository


def _schema_path(cfg: Config) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    name = "001_init_postgres.sql" if cfg.db_driver == "postgres" else "001_init_sqlite.sql"
    return os.path.join(root, "db", name)


async def init_database(cfg: Config) -> Database:
    """Connect and apply the schema for the configured backend."""
    db = get_database(cfg)
    await db.connect()
    with open(_schema_path(cfg), "r", encoding="utf-8") as fh:
        await db.executescript(fh.read())
    return db


async def run() -> None:
    cfg = load_config()
    log = setup_logging(os.getenv("LOG_LEVEL", "INFO"))

    if not cfg.bot_token:
        raise SystemExit("BOT_TOKEN is not set — copy .env.example to .env first.")

    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage

    from .handlers import build_router
    from .middlewares import (
        DependencyMiddleware,
        RateLimiter,
        RateLimitMiddleware,
    )
    from .scheduler import build_scheduler

    db = await init_database(cfg)
    repo = Repository(db)
    llm = LLMClient(
        api_key=cfg.llm_api_key,
        base_url=cfg.llm_base_url,
        model=cfg.llm_model,
        timeout=cfg.llm_timeout,
    )

    bot = Bot(token=cfg.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    deps = DependencyMiddleware(repo=repo, llm=llm, cfg=cfg)
    limiter = RateLimiter(cfg.rate_limit, cfg.rate_window)
    rate = RateLimitMiddleware(limiter, cfg.default_lang)

    dp.message.middleware(deps)
    dp.callback_query.middleware(deps)
    dp.message.middleware(rate)

    dp.include_router(build_router())

    scheduler = build_scheduler(bot, repo, cfg)
    scheduler.start()

    log.info("Bot starting (db=%s, model=%s)", cfg.db_driver, cfg.llm_model)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await db.close()
        logging.getLogger("tutor").info("Bot stopped")


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit) as exc:
        logging.getLogger("tutor").info("Shutdown: %s", exc)


if __name__ == "__main__":
    main()
