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
    """Parse a comma/space/semicolon separated list of telegram ids into ints."""
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
    # Global bot owners/superadmins (in addition to per-chat Telegram admins).
    admin_ids: List[int] = field(default_factory=list)
    tz: str = "Europe/Moscow"
    default_lang: str = "ru"

    # Database: driver = "sqlite" (local) or "postgres" (prod).
    db_driver: str = "sqlite"
    sqlite_path: str = "moderation.db"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "moderation"
    pg_password: str = "moderation"
    pg_database: str = "moderation"

    # Defaults applied to a chat the first time the bot sees it.
    captcha_timeout: int = 60          # seconds to solve the captcha
    warn_limit: int = 3               # active warns -> auto mute
    mute_duration: int = 3600         # seconds of auto mute at the warn threshold
    antiflood_limit: int = 5          # messages ...
    antiflood_window: int = 5         # ... per this many seconds -> mute

    # Rate limiting of the bot's own command handling (per user).
    rate_limit: int = 5
    rate_window: float = 3.0

    log_level: str = "INFO"

    def is_owner(self, user_id: int) -> bool:
        return user_id in self.admin_ids


def load_config() -> Config:
    """Build a Config from the current environment."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_ids=_parse_ids(os.getenv("ADMIN_IDS", "")),
        tz=os.getenv("TZ", "Europe/Moscow"),
        default_lang=os.getenv("DEFAULT_LANG", "ru").lower(),
        db_driver=os.getenv("DB_DRIVER", "sqlite").lower(),
        sqlite_path=os.getenv("SQLITE_PATH", "moderation.db"),
        pg_host=os.getenv("DB_HOST", "localhost"),
        pg_port=int(os.getenv("DB_PORT", "5432")),
        pg_user=os.getenv("DB_USER", "moderation"),
        pg_password=os.getenv("DB_PASSWORD", "moderation"),
        pg_database=os.getenv("DB_NAME", "moderation"),
        captcha_timeout=int(os.getenv("CAPTCHA_TIMEOUT", "60")),
        warn_limit=int(os.getenv("WARN_LIMIT", "3")),
        mute_duration=int(os.getenv("MUTE_DURATION", "3600")),
        antiflood_limit=int(os.getenv("ANTIFLOOD_LIMIT", "5")),
        antiflood_window=int(os.getenv("ANTIFLOOD_WINDOW", "5")),
        rate_limit=int(os.getenv("RATE_LIMIT", "5")),
        rate_window=float(os.getenv("RATE_WINDOW", "3.0")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
