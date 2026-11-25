"""Configuration loaded from environment / .env (no heavy deps)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

try:  # optional: load a .env file if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience only
    pass


def _parse_admin_ids(raw: str) -> List[int]:
    ids: List[int] = []
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk.lstrip("-").isdigit():
            ids.append(int(chunk))
    return ids


@dataclass
class Config:
    bot_token: str
    admin_ids: List[int] = field(default_factory=list)
    db_engine: str = "sqlite"          # "sqlite" | "postgres"
    db_dsn: str = "giveaway.db"        # sqlite path OR postgres DSN
    tz: str = "UTC"
    default_lang: str = "ru"
    rate_limit_seconds: float = 0.7
    log_level: str = "INFO"

    def is_admin(self, user_id: int) -> bool:
        return int(user_id) in self.admin_ids


def _build_postgres_dsn() -> str:
    # Prefer a full DSN if provided, else assemble from parts.
    dsn = os.getenv("DB_DSN") or os.getenv("DATABASE_URL")
    if dsn:
        return dsn
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "giveaway")
    user = os.getenv("DB_USER", "giveaway")
    password = os.getenv("DB_PASSWORD", "giveaway")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def load_config() -> Config:
    engine = os.getenv("DB_ENGINE", "sqlite").lower()
    if engine == "postgres":
        db_dsn = _build_postgres_dsn()
    else:
        db_dsn = os.getenv("DB_PATH", os.getenv("DB_DSN", "giveaway.db"))

    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        db_engine=engine,
        db_dsn=db_dsn,
        tz=os.getenv("TZ", "UTC"),
        default_lang=os.getenv("DEFAULT_LANG", "ru").lower(),
        rate_limit_seconds=float(os.getenv("RATE_LIMIT_SECONDS", "0.7")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
