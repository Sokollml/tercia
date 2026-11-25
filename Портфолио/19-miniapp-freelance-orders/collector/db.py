"""Запись сырых сообщений в Postgres (raw_messages).

Collector ТОЛЬКО вставляет строки. Дедуп — на уровне БД через UNIQUE(text_hash):
конфликт по хешу тихо игнорируется (ON CONFLICT DO NOTHING).

asyncpg импортируется лениво, чтобы модуль можно было импортировать в тестах
без установленного драйвера и без подключения к БД.
"""

from __future__ import annotations

from typing import Any, Optional

INSERT_SQL = """
INSERT INTO raw_messages (chat, author, text, text_hash, message_link, status)
VALUES ($1, $2, $3, $4, $5, 'pending')
ON CONFLICT (text_hash) DO NOTHING
RETURNING id
"""


async def connect(dsn: str) -> Any:
    """Открыть пул соединений asyncpg."""
    import asyncpg  # ленивый импорт

    return await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=4)


async def insert_raw_message(
    pool: Any,
    chat: str,
    author: Optional[str],
    text: str,
    text_hash: str,
    message_link: Optional[str],
) -> Optional[int]:
    """Вставить сообщение. Вернуть id или None, если дубликат отсеян БД."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            INSERT_SQL, chat, author, text, text_hash, message_link
        )
    return row["id"] if row else None
