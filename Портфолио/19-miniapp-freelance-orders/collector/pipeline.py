"""Чистая логика обработки сообщений (без Telegram и без БД).

Вынесено отдельно, чтобы покрыть тестами: на вход — «сырые» сообщения,
на выход — записи, готовые к вставке в raw_messages. Никакого I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Set

from dedup import text_hash
from prefilter import KEYWORDS, STOPWORDS, passes_prefilter


@dataclass
class RawMessage:
    """Сырьё из Telegram (или из теста)."""

    chat: str
    author: Optional[str]
    text: Optional[str]
    message_id: int


@dataclass
class Record:
    """Готовая к вставке запись raw_messages."""

    chat: str
    author: Optional[str]
    text: str
    text_hash: str
    message_link: Optional[str]


@dataclass
class Stats:
    seen: int = 0
    filtered_out: int = 0
    duplicates: int = 0
    accepted: int = 0


def build_message_link(chat: str, message_id: int) -> Optional[str]:
    """t.me/<chat>/<id> для публичных @username-чатов."""
    if not chat:
        return None
    handle = chat[1:] if chat.startswith("@") else chat
    if not handle or not handle.replace("_", "").isalnum():
        return None
    return f"https://t.me/{handle}/{message_id}"


def to_record(msg: RawMessage) -> Record:
    """Собрать Record из RawMessage (текст уже прошёл проверки)."""
    text = msg.text or ""
    return Record(
        chat=msg.chat,
        author=msg.author,
        text=text,
        text_hash=text_hash(text),
        message_link=build_message_link(msg.chat, msg.message_id),
    )


def filter_records(
    messages: Iterable[RawMessage],
    keywords: Optional[Iterable[str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    seen_hashes: Optional[Set[str]] = None,
) -> List[Record]:
    """Префильтр + внутрипроцессный дедуп -> список готовых Record.

    Финальный дедуп остаётся за БД (UNIQUE text_hash); здесь снимаем очевидные
    повторы в рамках одной пачки, чтобы не молотить БД зря.
    """
    kw = list(keywords) if keywords else list(KEYWORDS)
    sw = list(stopwords) if stopwords else list(STOPWORDS)
    seen: Set[str] = seen_hashes if seen_hashes is not None else set()
    out: List[Record] = []

    for msg in messages:
        if not passes_prefilter(msg.text, kw, sw):
            continue
        record = to_record(msg)
        if record.text_hash in seen:
            continue
        seen.add(record.text_hash)
        out.append(record)

    return out


def process_messages(
    messages: Iterable[RawMessage],
    keywords: Optional[Iterable[str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    on_record: Optional[Callable[[Record], bool]] = None,
    seen_hashes: Optional[Set[str]] = None,
) -> Stats:
    """Прогнать сообщения через префильтр + дедуп.

    - keywords/stopwords: переопределение списков (иначе дефолты из prefilter).
    - on_record(record) -> bool: колбэк вставки. Должен вернуть True, если
      запись реально добавлена (False -> считаем дубликатом на стороне БД).
      Если None — запись просто считается принятой (dry-run).
    - seen_hashes: внутрипроцессный дедуп в рамках одного запуска.
    """
    kw = list(keywords) if keywords else list(KEYWORDS)
    sw = list(stopwords) if stopwords else list(STOPWORDS)
    seen: Set[str] = seen_hashes if seen_hashes is not None else set()
    stats = Stats()

    for msg in messages:
        stats.seen += 1
        if not passes_prefilter(msg.text, kw, sw):
            stats.filtered_out += 1
            continue

        record = to_record(msg)
        if record.text_hash in seen:
            stats.duplicates += 1
            continue
        seen.add(record.text_hash)

        if on_record is None:
            stats.accepted += 1
            continue

        inserted = on_record(record)
        if inserted:
            stats.accepted += 1
        else:
            stats.duplicates += 1

    return stats
