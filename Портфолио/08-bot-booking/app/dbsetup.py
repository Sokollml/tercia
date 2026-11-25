"""Schema application and demo seeding.

Reads the plain-SQL migration matching the active driver and runs it, then
optionally seeds a master + a few services and upcoming slots so the bot is
usable immediately for a demo.
"""
from __future__ import annotations

import logging
import os

from .config import Config
from .db import Database
from .repository import Repository
from .services import now_ts

log = logging.getLogger("booking.dbsetup")

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")


def _schema_path(driver: str) -> str:
    name = "001_init_postgres.sql" if driver == "postgres" else "001_init_sqlite.sql"
    return os.path.join(DB_DIR, name)


async def apply_schema(db: Database) -> None:
    """Apply the migration file for the active driver."""
    path = _schema_path(db.driver)
    with open(path, "r", encoding="utf-8") as fh:
        script = fh.read()
    await db.executescript(script)  # type: ignore[attr-defined]
    log.info("schema applied from %s", os.path.basename(path))


async def seed_demo(repo: Repository, cfg: Config) -> None:
    """Create a master (first configured id) plus demo services and slots.

    Idempotent-ish: only seeds when there are no services yet for the master.
    """
    if not cfg.master_ids:
        log.warning("no MASTER_IDS configured; skipping demo seed")
        return
    master_id = cfg.master_ids[0]
    await repo.upsert_master(master_id, name="Demo Master", tz=cfg.tz, created_at=now_ts())

    if await repo.list_services(master_id):
        return  # already seeded

    await repo.add_service(master_id, "Haircut", 45, "25€")
    await repo.add_service(master_id, "Coloring", 120, "70€")
    await repo.add_service(master_id, "Styling", 30, "15€")

    # A handful of upcoming slots over the next few days.
    base = now_ts()
    hour = 3600
    offsets = [
        2 * hour,
        4 * hour,
        26 * hour,
        28 * hour,
        50 * hour,
    ]
    for off in offsets:
        start = base + off
        await repo.add_slot(master_id, start, start + hour)
    log.info("demo services and %d slots seeded for master %s", len(offsets), master_id)
