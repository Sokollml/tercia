"""Application entrypoint.

Wires together the bot, dispatcher, middlewares, database, scheduler and the
selected run mode (polling for local dev, webhook for production).

Run:
    python -m app.main
"""
from __future__ import annotations

import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import Config, load_config
from .db import get_database
from .dbsetup import apply_schema, seed_demo
from .handlers import build_router
from .logger import setup_logging
from .middlewares import LangMiddleware, RateLimitMiddleware
from .repository import Repository
from .scheduler import ReminderScheduler

log = logging.getLogger("booking.main")


async def _build(cfg: Config):
    """Construct shared objects (bot, dispatcher, repo, scheduler)."""
    if not cfg.bot_token:
        raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    db = get_database(cfg)
    await db.connect()
    await apply_schema(db)
    repo = Repository(db)
    await seed_demo(repo, cfg)

    lang_store: Dict[int, str] = {}

    dp = Dispatcher(storage=MemoryStorage())
    # Order matters: language/context first, then rate limiting.
    lang_mw = LangMiddleware(cfg.default_lang, cfg.master_ids, repo, cfg, lang_store)
    rate_mw = RateLimitMiddleware(cfg.rate_limit, cfg.rate_window)
    for observer in (dp.message, dp.callback_query):
        observer.middleware(lang_mw)
        observer.middleware(rate_mw)

    dp.include_router(build_router())

    scheduler = ReminderScheduler(bot, repo, cfg.tz, lang_store)
    return bot, dp, db, scheduler


async def run_polling(cfg: Config) -> None:
    bot, dp, db, scheduler = await _build(cfg)
    scheduler.start()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("Starting polling ...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await db.close()
        await bot.session.close()


async def run_webhook(cfg: Config) -> None:
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    bot, dp, db, scheduler = await _build(cfg)
    scheduler.start()

    await bot.set_webhook(
        url=cfg.webhook_url,
        secret_token=cfg.webhook_secret or None,
        drop_pending_updates=True,
    )
    log.info("Webhook set to %s", cfg.webhook_url)

    app = web.Application()

    async def health(_req):
        return web.Response(text="ok")

    app.router.add_get("/health", health)

    handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=cfg.webhook_secret or None
    )
    handler.register(app, path=cfg.webhook_path)
    setup_application(app, dp, bot=bot)

    async def _on_cleanup(_app):
        scheduler.shutdown()
        await db.close()
        await bot.session.close()

    app.on_cleanup.append(_on_cleanup)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=cfg.webapp_host, port=cfg.webapp_port)
    log.info("Serving webhook app on %s:%s", cfg.webapp_host, cfg.webapp_port)
    await site.start()
    # Run forever.
    await asyncio.Event().wait()


def main() -> None:
    cfg = load_config()
    setup_logging()
    log.info("Mode=%s Driver=%s TZ=%s", cfg.mode, cfg.db_driver, cfg.tz)
    if cfg.mode == "webhook":
        asyncio.run(run_webhook(cfg))
    else:
        asyncio.run(run_polling(cfg))


if __name__ == "__main__":
    main()
