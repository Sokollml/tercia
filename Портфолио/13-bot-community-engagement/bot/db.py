"""SQLAlchemy async models and session factory.

Cross-backend: SQLite locally (aiosqlite), PostgreSQL in production
(asyncpg). Same ORM models are used for both; ``BigInteger`` maps to
INTEGER on SQLite which is fine for Telegram ids.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import AsyncIterator, Optional

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lang: Mapped[str] = mapped_column(String(8), default="ru")

    # module toggles
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    xp_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    leaderboard_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_prompt_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # welcome
    welcome_text_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    welcome_text_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # xp / anti-abuse
    xp_per_message: Mapped[int] = mapped_column(Integer, default=5)
    xp_cooldown_sec: Mapped[int] = mapped_column(Integer, default=60)
    min_message_len: Mapped[int] = mapped_column(Integer, default=3)
    antiflood_window_sec: Mapped[int] = mapped_column(Integer, default=5)

    # schedules ("HH:MM" local time)
    daily_prompt_time: Mapped[str] = mapped_column(String(5), default="10:00")
    weekly_top_dow: Mapped[int] = mapped_column(Integer, default=0)  # 0=Mon
    weekly_top_time: Mapped[str] = mapped_column(String(5), default="12:00")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Member(Base):
    __tablename__ = "members"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)

    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_xp_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DailyPrompt(Base):
    __tablename__ = "daily_prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    kind: Mapped[str] = mapped_column(String(16), default="question")  # question|poll
    text_ru: Mapped[str] = mapped_column(Text)
    text_en: Mapped[str] = mapped_column(Text)
    options_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "a|b|c"
    options_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Event(Base):
    """Append-only log used for the weekly leaderboard and achievements."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    type: Mapped[str] = mapped_column(String(32), default="xp")  # xp|levelup|streak|join
    xp: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True, server_default=func.now())


# --- Engine / session helpers ----------------------------------------------

def make_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_async_engine(database_url, echo=echo, connect_args=connect_args)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_models(engine: AsyncEngine) -> None:
    """Create tables if they do not exist (used for SQLite / first run)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
