"""Async database access layer (SQLAlchemy 2.0, async engine).

Works with SQLite (``sqlite+aiosqlite``) and PostgreSQL (``postgresql+asyncpg``)
depending on ``Settings.database_url``. The repository functions here contain
the business-critical logic that the test-suite exercises:

* ``record_answer`` — inserts an answer while guaranteeing one answer per
  ``(poll_id, user_id)`` pair (double-answer protection), then bumps the
  aggregate season score in the same transaction.
"""
from __future__ import annotations

import random
from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Answer, Base, ChatSetting, Question, Quiz, Score, Season


class Database:
    """Owns the async engine and session factory."""

    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine: AsyncEngine = create_async_engine(url, echo=echo, future=True)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def create_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    def session(self) -> AsyncSession:
        return self.session_factory()


# --------------------------------------------------------------------------- #
# Seasons
# --------------------------------------------------------------------------- #
async def get_active_season(session: AsyncSession) -> Optional[Season]:
    res = await session.execute(
        select(Season).where(Season.is_active.is_(True)).order_by(Season.id.desc())
    )
    return res.scalars().first()


async def start_new_season(session: AsyncSession, title: str) -> Season:
    """Close any active season and open a fresh one."""
    await session.execute(
        update(Season).where(Season.is_active.is_(True)).values(
            is_active=False, ended_at=datetime.utcnow()
        )
    )
    season = Season(title=title, is_active=True)
    session.add(season)
    await session.commit()
    await session.refresh(season)
    return season


async def end_season(session: AsyncSession, season: Season) -> None:
    season.is_active = False
    season.ended_at = datetime.utcnow()
    await session.commit()


# --------------------------------------------------------------------------- #
# Questions
# --------------------------------------------------------------------------- #
async def add_question(
    session: AsyncSession,
    *,
    category: str,
    lang: str,
    text: str,
    options: Sequence[str],
    correct_index: int,
    explanation: Optional[str] = None,
) -> Question:
    question = Question(
        category=category,
        lang=lang,
        text=text,
        options=list(options),
        correct_index=correct_index,
        explanation=explanation,
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question


async def list_categories(session: AsyncSession, lang: Optional[str] = None) -> List[str]:
    stmt = select(Question.category).distinct().order_by(Question.category)
    if lang:
        stmt = stmt.where(Question.lang == lang)
    res = await session.execute(stmt)
    return [row[0] for row in res.all()]


async def pick_questions(
    session: AsyncSession,
    *,
    lang: str,
    category: Optional[str] = None,
    limit: int = 1,
    exclude_ids: Optional[Sequence[int]] = None,
) -> List[Question]:
    """Fetch up to ``limit`` random questions for the language/category."""
    stmt = select(Question).where(Question.lang == lang)
    if category:
        stmt = stmt.where(func.lower(Question.category) == category.lower())
    if exclude_ids:
        stmt = stmt.where(Question.id.notin_(list(exclude_ids)))
    res = await session.execute(stmt)
    questions = list(res.scalars().all())
    random.shuffle(questions)
    return questions[:limit]


async def count_questions(session: AsyncSession) -> int:
    res = await session.execute(select(func.count()).select_from(Question))
    return int(res.scalar_one())


# --------------------------------------------------------------------------- #
# Quizzes (published polls)
# --------------------------------------------------------------------------- #
async def create_quiz(
    session: AsyncSession,
    *,
    poll_id: str,
    chat_id: int,
    message_id: Optional[int],
    question_id: int,
    season_id: Optional[int],
    mode: str,
    correct_index: int,
    closes_at: Optional[datetime] = None,
) -> Quiz:
    quiz = Quiz(
        poll_id=poll_id,
        chat_id=chat_id,
        message_id=message_id,
        question_id=question_id,
        season_id=season_id,
        mode=mode,
        correct_index=correct_index,
        closes_at=closes_at,
    )
    session.add(quiz)
    await session.commit()
    await session.refresh(quiz)
    return quiz


async def get_quiz_by_poll(session: AsyncSession, poll_id: str) -> Optional[Quiz]:
    res = await session.execute(select(Quiz).where(Quiz.poll_id == poll_id))
    return res.scalars().first()


# --------------------------------------------------------------------------- #
# Answers + scoring (the core, well-tested path)
# --------------------------------------------------------------------------- #
async def record_answer(
    session: AsyncSession,
    *,
    quiz: Quiz,
    user_id: int,
    username: Optional[str],
    option_index: int,
    is_correct: bool,
    points: int,
) -> bool:
    """Record an answer exactly once per (poll, user).

    Returns ``True`` if this was a new answer that got stored (and scored),
    ``False`` if the user had already answered this poll (double answer).

    The unique constraint on ``(poll_id, user_id)`` is the source of truth: we
    optimistically insert and treat an :class:`IntegrityError` as "already
    answered", which is race-safe even across processes.
    """
    answer = Answer(
        quiz_id=quiz.id,
        poll_id=quiz.poll_id,
        user_id=user_id,
        username=username,
        option_index=option_index,
        is_correct=is_correct,
        points=points,
    )
    session.add(answer)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        return False

    if quiz.season_id is not None:
        await _bump_score(
            session,
            season_id=quiz.season_id,
            user_id=user_id,
            username=username,
            points=points,
            is_correct=is_correct,
        )

    await session.commit()
    return True


async def _bump_score(
    session: AsyncSession,
    *,
    season_id: int,
    user_id: int,
    username: Optional[str],
    points: int,
    is_correct: bool,
) -> None:
    res = await session.execute(
        select(Score).where(Score.season_id == season_id, Score.user_id == user_id)
    )
    score = res.scalars().first()
    if score is None:
        score = Score(
            season_id=season_id,
            user_id=user_id,
            username=username,
            points=points,
            correct_count=1 if is_correct else 0,
            total_count=1,
        )
        session.add(score)
    else:
        score.points += points
        score.total_count += 1
        if is_correct:
            score.correct_count += 1
        if username:
            score.username = username


async def get_leaderboard(
    session: AsyncSession, season_id: int, limit: int = 10
) -> List[Score]:
    res = await session.execute(
        select(Score)
        .where(Score.season_id == season_id)
        .order_by(Score.points.desc(), Score.correct_count.desc())
        .limit(limit)
    )
    return list(res.scalars().all())


async def get_user_score(
    session: AsyncSession, season_id: int, user_id: int
) -> Optional[Score]:
    res = await session.execute(
        select(Score).where(Score.season_id == season_id, Score.user_id == user_id)
    )
    return res.scalars().first()


# --------------------------------------------------------------------------- #
# Chat settings (language)
# --------------------------------------------------------------------------- #
async def get_chat_lang(
    session: AsyncSession, chat_id: int, default: str = "ru"
) -> str:
    res = await session.execute(
        select(ChatSetting).where(ChatSetting.chat_id == chat_id)
    )
    row = res.scalars().first()
    return row.lang if row else default


async def set_chat_lang(session: AsyncSession, chat_id: int, lang: str) -> None:
    res = await session.execute(
        select(ChatSetting).where(ChatSetting.chat_id == chat_id)
    )
    row = res.scalars().first()
    if row is None:
        session.add(ChatSetting(chat_id=chat_id, lang=lang))
    else:
        row.lang = lang
    await session.commit()


async def ensure_chat(
    session: AsyncSession, chat_id: int, default_lang: str = "ru"
) -> ChatSetting:
    """Return the chat's settings row, creating it if it does not exist yet."""
    res = await session.execute(
        select(ChatSetting).where(ChatSetting.chat_id == chat_id)
    )
    row = res.scalars().first()
    if row is None:
        row = ChatSetting(chat_id=chat_id, lang=default_lang)
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return row


async def set_daily(session: AsyncSession, chat_id: int, enabled: bool) -> None:
    """Enable/disable the scheduled daily question for a chat."""
    res = await session.execute(
        select(ChatSetting).where(ChatSetting.chat_id == chat_id)
    )
    row = res.scalars().first()
    if row is None:
        session.add(ChatSetting(chat_id=chat_id, daily_enabled=enabled))
    else:
        row.daily_enabled = enabled
    await session.commit()


async def get_daily_chats(session: AsyncSession) -> List[int]:
    """Chat ids subscribed to the scheduled daily question."""
    res = await session.execute(
        select(ChatSetting.chat_id).where(ChatSetting.daily_enabled.is_(True))
    )
    return [row[0] for row in res.all()]
