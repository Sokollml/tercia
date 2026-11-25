"""Shared pytest fixtures.

Provides a fresh in-memory SQLite database (with schema applied) and a
:class:`Repository` bound to it, so data-access tests run fast and isolated
without touching disk or a real Postgres.  Compatible with Python 3.9.
"""
from __future__ import annotations

import os

import pytest
import pytest_asyncio

from app.config import Config
from app.db import SqliteDatabase
from app.repository import Repository

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "db", "001_init_sqlite.sql")


@pytest.fixture
def config() -> Config:
    return Config(db_driver="sqlite", sqlite_path=":memory:", free_daily_limit=3)


@pytest_asyncio.fixture
async def db():
    database = SqliteDatabase(":memory:")
    await database.connect()
    with open(SCHEMA, "r", encoding="utf-8") as fh:
        await database.executescript(fh.read())
    try:
        yield database
    finally:
        await database.close()


@pytest_asyncio.fixture
async def repo(db) -> Repository:
    return Repository(db)
