"""Live-сборщик: userbot читает НОВЫЕ сообщения из публичных чатов config.yaml.

Только чтение. Никакой отправки, реакций, вступления в чаты. Троттлинг между
чатами/сообщениями. Сессия Telethon — в volume (см. TG_SESSION), не в репозитории.

Запуск:
    python collector.py --config config.yaml

БАН-РИСКИ: используй ОТДЕЛЬНЫЙ аккаунт, не основной. См. README.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from typing import List

from config import Env, CollectorConfig, load_config, load_env
from db import connect, insert_raw_message
from pipeline import RawMessage, filter_records
from prefilter import STOPWORDS

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("collector")


async def fetch_new_messages(client, chat: str, min_id: int, limit: int = 100):
    """Прочитать новые сообщения из одного чата (id > min_id). Только чтение."""
    out: List[RawMessage] = []
    async for message in client.iter_messages(chat, min_id=min_id, limit=limit):
        if not message.message:
            continue
        author = None
        sender = await message.get_sender()
        if sender is not None:
            author = getattr(sender, "username", None)
        out.append(
            RawMessage(
                chat=chat,
                author=author,
                text=message.message,
                message_id=message.id,
            )
        )
    return out


async def run(cfg: CollectorConfig, env: Env) -> None:
    from telethon import TelegramClient  # ленивый импорт

    stopwords = list(STOPWORDS) + list(cfg.stopwords_extra)
    keywords = cfg.keywords or None

    pool = await connect(env.db_dsn)
    client = TelegramClient(env.session, env.api_id, env.api_hash)
    await client.start(phone=env.phone)
    log.info("Клиент запущен. Чатов в конфиге: %d", len(cfg.chats))

    last_ids = {chat: 0 for chat in cfg.chats}

    try:
        while True:
            for chat in cfg.chats:
                try:
                    messages = await fetch_new_messages(
                        client, chat, min_id=last_ids[chat]
                    )
                except Exception as exc:  # noqa: BLE001 — один битый чат не валит цикл
                    log.warning("Чат %s: ошибка чтения: %s", chat, exc)
                    continue

                if messages:
                    last_ids[chat] = max(m.message_id for m in messages)

                # Синхронно: префильтр + внутрипроцессный дедуп -> записи.
                records = filter_records(
                    messages, keywords=keywords, stopwords=stopwords
                )

                # Асинхронно: вставка. БД сама отсечёт дубли по UNIQUE(text_hash).
                accepted = 0
                for rec in records:
                    new_id = await insert_raw_message(
                        pool, rec.chat, rec.author, rec.text,
                        rec.text_hash, rec.message_link,
                    )
                    if new_id is not None:
                        accepted += 1
                    await asyncio.sleep(cfg.throttle.between_messages_sec)

                log.info(
                    "Чат %s: получено %d, к вставке %d, вставлено %d",
                    chat, len(messages), len(records), accepted,
                )
                await asyncio.sleep(cfg.throttle.between_chats_sec)

            await asyncio.sleep(env.poll_interval)
    finally:
        await client.disconnect()
        await pool.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live-сборщик фриланс-заказов")
    parser.add_argument(
        "--config",
        default=os.getenv("COLLECTOR_CONFIG", "config.yaml"),
        help="путь к config.yaml",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    env = load_env()
    asyncio.run(run(cfg, env))


if __name__ == "__main__":
    main()
