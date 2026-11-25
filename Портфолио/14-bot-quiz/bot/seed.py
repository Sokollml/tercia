"""Import seed questions from a JSON file into the questions bank.

Idempotent: a question is skipped if an identical (lang, text) already exists,
so re-running the importer will not create duplicates.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from .db import Database
from .models import Question

logger = logging.getLogger(__name__)

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_questions.json"


def _validate(item: dict) -> Optional[str]:
    required = ("category", "lang", "text", "options", "correct_index")
    for key in required:
        if key not in item:
            return f"missing key '{key}'"
    if not isinstance(item["options"], list) or not (2 <= len(item["options"]) <= 10):
        return "options must be a list of 2..10 entries"
    if not isinstance(item["correct_index"], int) or not (
        0 <= item["correct_index"] < len(item["options"])
    ):
        return "correct_index out of range"
    return None


async def import_seed(db: Database, path: Optional[Path] = None) -> int:
    """Load questions from ``path`` (defaults to bundled seed). Returns count added."""
    path = path or DEFAULT_SEED_PATH
    if not path.exists():
        logger.warning("Seed file not found: %s", path)
        return 0

    data = json.loads(path.read_text(encoding="utf-8"))
    added = 0
    async with db.session() as session:
        for item in data:
            problem = _validate(item)
            if problem:
                logger.warning("Skipping seed item (%s): %r", problem, item.get("text"))
                continue

            existing = await session.execute(
                select(Question.id).where(
                    Question.lang == item["lang"], Question.text == item["text"]
                )
            )
            if existing.first():
                continue

            session.add(
                Question(
                    category=item["category"],
                    lang=item["lang"],
                    text=item["text"],
                    options=list(item["options"]),
                    correct_index=int(item["correct_index"]),
                    explanation=item.get("explanation"),
                )
            )
            added += 1
        await session.commit()

    logger.info("Seed import complete: %d new questions from %s", added, path)
    return added
