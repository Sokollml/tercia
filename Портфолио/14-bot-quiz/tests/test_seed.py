"""Tests for the JSON seed importer (idempotency and validation)."""
from __future__ import annotations

import json

import pytest

from bot import db as repo
from bot.seed import import_seed


@pytest.mark.asyncio
async def test_seed_import_is_idempotent(database, tmp_path):
    seed = [
        {
            "category": "История",
            "lang": "ru",
            "text": "Год Крещения Руси?",
            "options": ["882", "988"],
            "correct_index": 1,
            "explanation": "988",
        },
        {  # invalid: correct_index out of range -> skipped
            "category": "Bad",
            "lang": "en",
            "text": "bad",
            "options": ["a", "b"],
            "correct_index": 9,
        },
    ]
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(seed), encoding="utf-8")

    added_first = await import_seed(database, path)
    added_second = await import_seed(database, path)

    assert added_first == 1  # one valid, one skipped
    assert added_second == 0  # re-import adds nothing

    async with database.session() as session:
        total = await repo.count_questions(session)
    assert total == 1


@pytest.mark.asyncio
async def test_bundled_seed_file_loads(database):
    # The shipped data/seed_questions.json must import cleanly.
    added = await import_seed(database)
    assert added > 0
    async with database.session() as session:
        cats = await repo.list_categories(session)
    assert cats  # at least one category present
