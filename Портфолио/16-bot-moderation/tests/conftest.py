"""Shared pytest fixtures and helpers."""
from __future__ import annotations

import os
import sys
from typing import List, Tuple

import pytest_asyncio

# Make the project root importable when running pytest from anywhere.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.config import Config  # noqa: E402
from app.db import get_database  # noqa: E402
from app.dbsetup import apply_schema  # noqa: E402
from app.repository import Repository  # noqa: E402


def make_config(**overrides) -> Config:
    base = dict(
        bot_token="test",
        db_driver="sqlite",
        sqlite_path=":memory:",
        default_lang="ru",
        captcha_timeout=60,
        warn_limit=3,
        mute_duration=3600,
        antiflood_limit=5,
        antiflood_window=5,
    )
    base.update(overrides)
    return Config(**base)


@pytest_asyncio.fixture
async def repo():
    """A Repository backed by a fresh in-memory SQLite database."""
    cfg = make_config()
    db = get_database(cfg)
    await db.connect()
    await apply_schema(db)
    try:
        yield Repository(db, cfg)
    finally:
        await db.close()


@pytest_asyncio.fixture
def fake_bot():
    """A fresh FakeBot per test."""
    return FakeBot()


class FakeBot:
    """Minimal async stand-in for aiogram's Bot, recording moderation calls."""

    def __init__(self) -> None:
        self.banned: List[Tuple[int, int]] = []
        self.unbanned: List[Tuple[int, int]] = []
        self.deleted: List[Tuple[int, int]] = []

    async def ban_chat_member(self, chat_id: int, user_id: int, **kwargs):
        self.banned.append((chat_id, user_id))

    async def unban_chat_member(self, chat_id: int, user_id: int, **kwargs):
        self.unbanned.append((chat_id, user_id))

    async def delete_message(self, chat_id: int, message_id: int, **kwargs):
        self.deleted.append((chat_id, message_id))
