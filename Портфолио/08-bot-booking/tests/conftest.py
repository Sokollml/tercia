"""Shared pytest fixtures.

Spins up an in-memory SQLite database with the real schema and a seeded master,
so repository behaviour is exercised exactly as in production (minus the driver).
"""
from __future__ import annotations

import os
import sys

import pytest
import pytest_asyncio

# Make the project importable when running `pytest` from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SqliteDatabase  # noqa: E402
from app.dbsetup import apply_schema  # noqa: E402
from app.repository import Repository  # noqa: E402
from app.services import now_ts  # noqa: E402

MASTER_ID = 111
CLIENT_A = 222
CLIENT_B = 333


@pytest_asyncio.fixture
async def repo():
    """A Repository backed by a fresh in-memory SQLite DB with schema applied."""
    db = SqliteDatabase(":memory:")
    await db.connect()
    await apply_schema(db)
    repository = Repository(db)
    await repository.upsert_master(MASTER_ID, "Test Master", "Europe/Moscow", now_ts())
    try:
        yield repository
    finally:
        await db.close()
