"""Shared pytest fixtures: an in-memory SQLite async DB."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import StaticPool

# Make the project root importable (so `import bot...` works).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bot.db import Base, make_engine  # noqa: E402


@pytest_asyncio.fixture
async def session_factory():
    # Shared in-memory DB across sessions via StaticPool.
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def session(session_factory):
    async with session_factory() as s:
        yield s
