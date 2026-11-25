"""Application configuration loaded from environment variables / .env.

Python 3.9 compatible (uses ``from __future__ import annotations`` and typing).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

try:  # optional dependency, app still works if it is missing
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dotenv is an optional convenience
    def load_dotenv(*args, **kwargs):  # type: ignore
        return False


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


def _as_bool(raw: Optional[str], default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


@dataclass
class Settings:
    """Runtime configuration.

    ``db_engine`` selects the storage backend: ``sqlite`` (default, good for
    local development) or ``postgres`` (production).
    """

    bot_token: str = ""
    admin_ids: List[int] = field(default_factory=list)
    default_lang: str = "ru"
    tz: str = "Europe/Moscow"

    db_engine: str = "sqlite"
    sqlite_path: str = "data/quiz.db"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "quizbot"
    db_user: str = "quizbot"
    db_password: str = "quizbot"

    # Gameplay tuning
    base_points: int = 10
    speed_bonus_max: int = 5
    speed_window_seconds: int = 60
    poll_open_seconds: int = 60  # how long a quiz poll accepts answers
    marathon_size: int = 5
    marathon_gap_seconds: int = 20
    blitz_size: int = 5
    blitz_gap_seconds: int = 8

    # Rate limiting (per-user command throttling)
    rate_limit_seconds: float = 1.0

    daily_cron_hour: int = 12
    daily_cron_minute: int = 0

    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        """SQLAlchemy async database URL."""
        if self.db_engine == "postgres":
            return (
                f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        return f"sqlite+aiosqlite:///{self.sqlite_path}"

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids


def load_settings(env_file: Optional[str] = ".env") -> Settings:
    """Load :class:`Settings` from the environment (and optional .env file)."""
    if env_file:
        load_dotenv(env_file)

    def _int(name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)))
        except (TypeError, ValueError):
            return default

    def _float(name: str, default: float) -> float:
        try:
            return float(os.getenv(name, str(default)))
        except (TypeError, ValueError):
            return default

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS")),
        default_lang=os.getenv("DEFAULT_LANG", "ru").lower(),
        tz=os.getenv("TZ", "Europe/Moscow"),
        db_engine=os.getenv("DB_ENGINE", "sqlite").lower(),
        sqlite_path=os.getenv("SQLITE_PATH", "data/quiz.db"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=_int("DB_PORT", 5432),
        db_name=os.getenv("DB_NAME", "quizbot"),
        db_user=os.getenv("DB_USER", "quizbot"),
        db_password=os.getenv("DB_PASSWORD", "quizbot"),
        base_points=_int("BASE_POINTS", 10),
        speed_bonus_max=_int("SPEED_BONUS_MAX", 5),
        speed_window_seconds=_int("SPEED_WINDOW_SECONDS", 60),
        poll_open_seconds=_int("POLL_OPEN_SECONDS", 60),
        marathon_size=_int("MARATHON_SIZE", 5),
        marathon_gap_seconds=_int("MARATHON_GAP_SECONDS", 20),
        blitz_size=_int("BLITZ_SIZE", 5),
        blitz_gap_seconds=_int("BLITZ_GAP_SECONDS", 8),
        rate_limit_seconds=_float("RATE_LIMIT_SECONDS", 1.0),
        daily_cron_hour=_int("DAILY_CRON_HOUR", 12),
        daily_cron_minute=_int("DAILY_CRON_MINUTE", 0),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
