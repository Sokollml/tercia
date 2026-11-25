"""Разовая выгрузка ИСТОРИИ публичных чатов в raw_messages.

Отличие от collector.py: не крутится в цикле, а один раз тянет последние
`history_limit` сообщений из каждого чата, прогоняет через тот же префильтр/дедуп
и вставляет в БД. Удобно для «холодного старта».

Только чтение. Троттлинг такой же. Запуск:
    python export_history.py --config config.yaml --limit 200
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
log = logging.getLogger("export_history")


async def fetch_history(client, chat: str, limit: int) -> List[RawMessage]:
    out: List[RawMessage] = []
    async for message in client.iter_messages(chat, limit=limit):
        if not message.message:
            continue
        sender = await message.get_sender()
        author = getattr(sender, "username", None) if sender else None
        out.append(
            RawMessage(
                chat=chat,
                author=author,
                text=message.message,
                message_id=message.id,
            )
        )
    return out


async def run(cfg: CollectorConfig, env: Env, limit: int) -> None:
    from telethon import TelegramClient  # ленивый импорт

    stopwords = list(STOPWORDS) + list(cfg.stopwords_extra)
    keywords = cfg.keywords or None

    pool = await connect(env.db_dsn)
    client = TelegramClient(env.session, env.api_id, env.api_hash)
    await client.start(phone=env.phone)

    total = 0
    try:
        for chat in cfg.chats:
            try:
                messages = await fetch_history(client, chat, limit)
            except Exception as exc:  # noqa: BLE001
                log.warning("Чат %s: ошибка: %s", chat, exc)
                continue

            records = filter_records(
                messages, keywords=keywords, stopwords=stopwords
            )
            accepted = 0
            for rec in records:
                new_id = await insert_raw_message(
                    pool, rec.chat, rec.author, rec.text,
                    rec.text_hash, rec.message_link,
                )
                if new_id is not None:
                    accepted += 1
                await asyncio.sleep(cfg.throttle.between_messages_sec)

            total += accepted
            log.info(
                "Чат %s: история %d, к вставке %d, вставлено %d",
                chat, len(messages), len(records), accepted,
            )
            await asyncio.sleep(cfg.throttle.between_chats_sec)
    finally:
        await client.disconnect()
        await pool.close()

    log.info("Готово. Всего вставлено: %d", total)


def main() -> None:
    parser = argparse.ArgumentParser(description="Разовая выгрузка истории")
    parser.add_argument(
        "--config", default=os.getenv("COLLECTOR_CONFIG", "config.yaml")
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    env = load_env()
    limit = args.limit or cfg.history_limit or env.history_limit
    asyncio.run(run(cfg, env, limit))


if __name__ == "__main__":
    main()
