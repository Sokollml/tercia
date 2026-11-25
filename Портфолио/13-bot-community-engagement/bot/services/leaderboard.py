"""Leaderboard calculations (weekly from events, all-time from members)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Event, Member


@dataclass
class LeaderRow:
    user_id: int
    name: str
    value: int  # xp for the period (weekly) or total xp (all-time)
    position: int


def week_start(now: datetime) -> datetime:
    """Monday 00:00 of the current week for ``now``."""
    monday = now - timedelta(days=now.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


async def weekly_top(
    session: AsyncSession,
    chat_id: int,
    now: Optional[datetime] = None,
    limit: int = 10,
) -> List[LeaderRow]:
    """Sum XP from the ``events`` log since Monday for a chat."""
    now = now or datetime.utcnow()
    start = week_start(now)

    stmt = (
        select(Event.user_id, func.sum(Event.xp).label("total"))
        .where(
            Event.chat_id == chat_id,
            Event.type == "xp",
            Event.created_at >= start,
        )
        .group_by(Event.user_id)
        .order_by(desc("total"))
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return await _attach_names(session, chat_id, rows)


async def alltime_top(
    session: AsyncSession,
    chat_id: int,
    limit: int = 10,
) -> List[LeaderRow]:
    stmt = (
        select(Member.user_id, Member.xp, Member.username, Member.full_name)
        .where(Member.chat_id == chat_id)
        .order_by(desc(Member.xp))
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    result: List[LeaderRow] = []
    for pos, row in enumerate(rows, start=1):
        name = row.username or row.full_name or str(row.user_id)
        result.append(LeaderRow(row.user_id, name, int(row.xp or 0), pos))
    return result


async def member_position(session: AsyncSession, chat_id: int, user_id: int) -> int:
    """1-based all-time rank position of a member by XP (0 if unknown)."""
    me = (
        await session.execute(
            select(Member.xp).where(
                Member.chat_id == chat_id, Member.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if me is None:
        return 0
    ahead = (
        await session.execute(
            select(func.count()).where(
                Member.chat_id == chat_id, Member.xp > me
            )
        )
    ).scalar_one()
    return int(ahead) + 1


async def _attach_names(session: AsyncSession, chat_id: int, rows) -> List[LeaderRow]:
    result: List[LeaderRow] = []
    for pos, row in enumerate(rows, start=1):
        member = (
            await session.execute(
                select(Member).where(
                    Member.chat_id == chat_id, Member.user_id == row.user_id
                )
            )
        ).scalar_one_or_none()
        if member is not None:
            name = member.username or member.full_name or str(row.user_id)
        else:
            name = str(row.user_id)
        result.append(LeaderRow(row.user_id, name, int(row.total or 0), pos))
    return result
