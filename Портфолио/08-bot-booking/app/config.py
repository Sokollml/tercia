"""Application configuration loaded from environment variables.

Kept dependency-light so it can be imported in tests without a running bot.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

try:
    # python-dotenv is optional at import time (e.g. in CI/tests).
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience only
    pass


def _parse_ids(raw: str) -> List[int]:
    """Parse a comma/space separated list of telegram ids into ints."""
    ids: List[int] = []
    for chunk in raw.replace(";", ",").replace(" ", ",").split(","):
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
    """Typed view over environment variables."""

    bot_token: str = ""
    master_ids: List[int] = field(default_factory=list)
    tz: str = "Europe/Moscow"
    default_lang: str = "ru"

    # Run mode: "polling" (local) or "webhook" (prod).
    mode: str = "polling"

    # Webhook settings (used only when mode == "webhook").
    webhook_host: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080

    # Database: driver = "sqlite" (local) or "postgres" (prod).
    db_driver: str = "sqlite"
    sqlite_path: str = "booking.db"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "booking"
    pg_password: str = "booking"
    pg_database: str = "booking"

    # Rate limiting: max messages per window (seconds).
    rate_limit: int = 5
    rate_window: float = 3.0

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_host.rstrip('/')}{self.webhook_path}"

    def is_master(self, user_id: int) -> bool:
        return user_id in self.master_ids


def load_config() -> Config:
    """Build a Config from the current environment."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        master_ids=_parse_ids(os.getenv("MASTER_IDS", "")),
        tz=os.getenv("TZ", "Europe/Moscow"),
        default_lang=os.getenv("DEFAULT_LANG", "ru").lower(),
        mode=os.getenv("MODE", "polling").lower(),
        webhook_host=os.getenv("WEBHOOK_HOST", ""),
        webhook_path=os.getenv("WEBHOOK_PATH", "/webhook"),
        webhook_secret=os.getenv("WEBHOOK_SECRET", ""),
        webapp_host=os.getenv("WEBAPP_HOST", "0.0.0.0"),
        webapp_port=int(os.getenv("WEBAPP_PORT", "8080")),
        db_driver=os.getenv("DB_DRIVER", "sqlite").lower(),
        sqlite_path=os.getenv("SQLITE_PATH", "booking.db"),
        pg_host=os.getenv("DB_HOST", "localhost"),
        pg_port=int(os.getenv("DB_PORT", "5432")),
        pg_user=os.getenv("DB_USER", "booking"),
        pg_password=os.getenv("DB_PASSWORD", "booking"),
        pg_database=os.getenv("DB_NAME", "booking"),
        rate_limit=int(os.getenv("RATE_LIMIT", "5")),
        rate_window=float(os.getenv("RATE_WINDOW", "3.0")),
    )
