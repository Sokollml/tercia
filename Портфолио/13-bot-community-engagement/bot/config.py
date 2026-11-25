"""Application configuration loaded from environment (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _parse_admin_ids(raw: Optional[str]) -> List[int]:
    if not raw:
        return []
    ids: List[int] = []
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.append(int(chunk))
        except ValueError:
            continue
    return ids


@dataclass
class Config:
    bot_token: str = ""
    db_engine: str = "sqlite"  # "sqlite" or "postgres"
    db_path: str = "data/bot.db"  # for sqlite
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "engagement"
    db_user: str = "engagement"
    db_password: str = "engagement"
    tz: str = "UTC"
    admin_ids: List[int] = field(default_factory=list)
    default_lang: str = "ru"
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL for the selected backend."""
        if self.db_engine.lower() in {"postgres", "postgresql"}:
            return (
                f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        # sqlite (async)
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def is_sqlite(self) -> bool:
        return self.db_engine.lower() not in {"postgres", "postgresql"}


def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        db_engine=os.getenv("DB_ENGINE", "sqlite"),
        db_path=os.getenv("DB_PATH", "data/bot.db"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=_get_int("DB_PORT", 5432),
        db_name=os.getenv("DB_NAME", "engagement"),
        db_user=os.getenv("DB_USER", "engagement"),
        db_password=os.getenv("DB_PASSWORD", "engagement"),
        tz=os.getenv("TZ", "UTC"),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS")),
        default_lang=os.getenv("DEFAULT_LANG", "ru"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
