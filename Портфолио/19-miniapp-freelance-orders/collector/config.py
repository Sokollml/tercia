"""Загрузка config.yaml + .env для collector-а.

Ничего не подключает при импорте — только читает файлы. Удобно тестировать.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv не обязателен в тестах
    def load_dotenv(*_a, **_k):  # type: ignore
        return False


@dataclass
class Throttle:
    between_chats_sec: float = 5.0
    between_messages_sec: float = 0.5


@dataclass
class CollectorConfig:
    chats: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    stopwords_extra: List[str] = field(default_factory=list)
    throttle: Throttle = field(default_factory=Throttle)
    history_limit: int = 200


def load_config(path: str) -> CollectorConfig:
    """Прочитать config.yaml в типизированный объект."""
    with open(path, "r", encoding="utf-8") as fh:
        data: Dict[str, Any] = yaml.safe_load(fh) or {}

    thr = data.get("throttle") or {}
    return CollectorConfig(
        chats=list(data.get("chats") or []),
        keywords=list(data.get("keywords") or []),
        stopwords_extra=list(data.get("stopwords_extra") or []),
        throttle=Throttle(
            between_chats_sec=float(thr.get("between_chats_sec", 5.0)),
            between_messages_sec=float(thr.get("between_messages_sec", 0.5)),
        ),
        history_limit=int(data.get("history_limit", 200)),
    )


@dataclass
class Env:
    api_id: int
    api_hash: str
    phone: str
    session: str
    db_dsn: str
    history_limit: int
    poll_interval: int


def load_env() -> Env:
    """Собрать настройки окружения из .env / переменных среды."""
    load_dotenv()
    return Env(
        api_id=int(os.getenv("TG_API_ID", "0")),
        api_hash=os.getenv("TG_API_HASH", ""),
        phone=os.getenv("TG_PHONE", ""),
        session=os.getenv("TG_SESSION", "collector.session"),
        db_dsn=(
            "postgresql://{user}:{pwd}@{host}:{port}/{db}".format(
                user=os.getenv("DB_USER", "freelance"),
                pwd=os.getenv("DB_PASSWORD", ""),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                db=os.getenv("DB_NAME", "freelance_orders"),
            )
        ),
        history_limit=int(os.getenv("HISTORY_LIMIT", "200")),
        poll_interval=int(os.getenv("POLL_INTERVAL", "60")),
    )
