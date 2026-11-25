"""Application configuration loaded from environment variables.

Kept dependency-light so it can be imported in tests without a running bot or
network access.  Compatible with Python 3.9 (uses ``Optional`` / ``List`` from
``typing`` rather than PEP 604 unions at runtime).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

try:
    # python-dotenv is optional at import time (e.g. in CI / tests).
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience only
    pass


@dataclass
class Config:
    """Typed view over environment variables."""

    bot_token: str = ""
    tz: str = "Europe/Moscow"
    default_lang: str = "ru"

    # Database: driver = "sqlite" (local) or "postgres" (prod).
    db_driver: str = "sqlite"
    sqlite_path: str = "tutor.db"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "tutor"
    pg_password: str = "tutor"
    pg_database: str = "tutor"

    # LLM (OpenAI-compatible chat/completions endpoint).
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 30.0

    # Rate limiting: max messages per window (seconds).
    rate_limit: int = 5
    rate_window: float = 3.0

    # Free-tier daily cap on LLM-backed corrections per user.
    free_daily_limit: int = 30

    def build_dsn(self) -> str:
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_database}"
        )


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def load_config() -> Config:
    """Build a :class:`Config` from the current environment."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        tz=os.getenv("TZ", "Europe/Moscow"),
        default_lang=os.getenv("DEFAULT_LANG", "ru").lower(),
        db_driver=os.getenv("DB_DRIVER", "sqlite").lower(),
        sqlite_path=os.getenv("SQLITE_PATH", "tutor.db"),
        pg_host=os.getenv("DB_HOST", "localhost"),
        pg_port=_get_int("DB_PORT", 5432),
        pg_user=os.getenv("DB_USER", "tutor"),
        pg_password=os.getenv("DB_PASSWORD", "tutor"),
        pg_database=os.getenv("DB_NAME", "tutor"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        llm_timeout=_get_float("LLM_TIMEOUT", 30.0),
        rate_limit=_get_int("RATE_LIMIT", 5),
        rate_window=_get_float("RATE_WINDOW", 3.0),
        free_daily_limit=_get_int("FREE_DAILY_LIMIT", 30),
    )


# Supported learning languages (code -> display name in both UI languages).
LEARN_LANGUAGES = {
    "en": {"ru": "Английский", "en": "English"},
    "de": {"ru": "Немецкий", "en": "German"},
    "es": {"ru": "Испанский", "en": "Spanish"},
    "fr": {"ru": "Французский", "en": "French"},
    "it": {"ru": "Итальянский", "en": "Italian"},
}

# CEFR levels offered during onboarding.
LEVELS = ("A1", "A2", "B1", "B2", "C1")
