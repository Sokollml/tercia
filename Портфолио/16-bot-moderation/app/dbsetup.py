"""Schema application helper.

Reads the plain-SQL migration matching the active driver and runs it.
"""
from __future__ import annotations

import logging
import os

from .db import Database

log = logging.getLogger("moderation.dbsetup")

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")


def schema_path(driver: str) -> str:
    name = "001_init_postgres.sql" if driver == "postgres" else "001_init_sqlite.sql"
    return os.path.join(DB_DIR, name)


async def apply_schema(db: Database) -> None:
    """Apply the migration file for the active driver."""
    path = schema_path(db.driver)
    with open(path, "r", encoding="utf-8") as fh:
        script = fh.read()
    await db.executescript(script)
    log.info("schema applied from %s", os.path.basename(path))
