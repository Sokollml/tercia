"""Entry point: wires config, DB, handlers, scheduler and starts polling."""
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import load_config
from bot.db import init_models, make_engine, make_session_factory
from bot.handlers import register_handlers
from bot.middlewares import DbSessionMiddleware
from bot.scheduler import build_scheduler
from bot.services.prompts import seed_prompts

log = logging.getLogger(__name__)


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


async def run() -> None:
    config = load_config()
    setup_logging(config.log_level)

    if not config.bot_token:
        raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    # Ensure sqlite data directory exists.
    if config.is_sqlite:
        os.makedirs(os.path.dirname(config.db_path) or ".", exist_ok=True)

    engine = make_engine(config.database_url)
    session_factory = make_session_factory(engine)

    # Create tables (SQLite / first run). For Postgres you may prefer db/ SQL.
    await init_models(engine)
    async with session_factory() as session:
        added = await seed_prompts(session)
        await session.commit()
        if added:
            log.info("Seeded %s built-in prompts", added)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp["config"] = config

    dp.update.middleware(DbSessionMiddleware(session_factory))
    register_handlers(dp)

    scheduler = build_scheduler(
        bot,
        session_factory,
        tz=config.tz,
        weekly_dow=0,
        weekly_time="12:00",
    )
    scheduler.start()
    log.info("Scheduler started (tz=%s)", config.tz)

    try:
        log.info("Bot starting polling...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await engine.dispose()


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit) as exc:
        log.info("Stopped: %s", exc)


if __name__ == "__main__":
    main()
