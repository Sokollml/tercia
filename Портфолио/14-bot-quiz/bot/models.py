"""SQLAlchemy ORM models.

The canonical schema also lives as raw DDL in ``db/schema_postgres.sql`` and
``db/schema_sqlite.sql``; these ORM models mirror it and are what the app uses
to create tables (``Base.metadata.create_all``) on both SQLite and PostgreSQL.

Python 3.9 compatible: we avoid PEP 604 unions and ``list[...]`` builtins in
favour of ``typing.Optional`` / ``typing.List``.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    scores: Mapped[List["Score"]] = relationship(back_populates="season")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lang: Mapped[str] = mapped_column(String(2), nullable=False, default="ru", index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # options stored as a JSON array of strings
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class Quiz(Base):
    """A single question published to a chat as a Telegram quiz poll."""

    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poll_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )
    season_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True
    )
    mode: Mapped[str] = mapped_column(String(16), nullable=False, default="daily")
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    closes_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    answers: Mapped[List["Answer"]] = relationship(back_populates="quiz")


class Answer(Base):
    """A user's answer to a quiz poll. Unique per (poll_id, user_id)."""

    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("poll_id", "user_id", name="uq_answer_poll_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    poll_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    quiz: Mapped["Quiz"] = relationship(back_populates="answers")


class Score(Base):
    """Aggregated per-user, per-season standings (season leaderboard)."""

    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("season_id", "user_id", name="uq_score_season_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    season: Mapped["Season"] = relationship(back_populates="scores")


class ChatSetting(Base):
    """Per-chat preferences (language and scheduled-quiz subscription).

    A row is created the first time the bot interacts with a chat (a quiz is
    published or ``/lang`` is used). ``daily_enabled`` marks chats that should
    receive the scheduled daily question.
    """

    __tablename__ = "chat_settings"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lang: Mapped[str] = mapped_column(String(2), nullable=False, default="ru")
    daily_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
