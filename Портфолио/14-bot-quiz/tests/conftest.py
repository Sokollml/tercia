"""Shared pytest fixtures.

Tests run against a real (temporary, file-backed) SQLite database through the
same async repository code the bot uses in production, so the double-answer
guard and score aggregation are exercised end to end.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Make the project importable when pytest is run from the project root.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bot.db import Database  # noqa: E402


@pytest_asyncio.fixture()
async def database(tmp_path):
    db_path = tmp_path / "test_quiz.db"
    db = Database(f"sqlite+aiosqlite:///{db_path}")
    await db.create_all()
    try:
        yield db
    finally:
        await db.dispose()
