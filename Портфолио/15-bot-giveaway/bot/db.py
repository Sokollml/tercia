"""Async database layer supporting SQLite (dev) and PostgreSQL (prod).

The engine is chosen at runtime from :class:`bot.config.Config`. Driver
imports are lazy so the app only needs the driver for the engine it uses.

All SQL is written with ``?`` placeholders and translated to ``$1, $2 ...``
for asyncpg by :func:`_pg` so handler code stays engine-agnostic.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _pg(sql: str) -> str:
    """Convert ``?`` placeholders to PostgreSQL ``$1, $2, ...``."""
    counter = {"n": 0}

    def repl(_m):
        counter["n"] += 1
        return f"${counter['n']}"

    return re.sub(r"\?", repl, sql)


class Database:
    """Thin async repository over the two supported engines."""

    def __init__(self, engine: str, dsn: str):
        self.engine = engine.lower()
        self.dsn = dsn
        self._sqlite = None  # aiosqlite connection
        self._pool = None    # asyncpg pool

    # ---- lifecycle -----------------------------------------------------
    async def connect(self) -> None:
        if self.engine == "postgres":
            import asyncpg  # lazy

            self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)
        else:
            import aiosqlite  # lazy

            self._sqlite = await aiosqlite.connect(self.dsn)
            self._sqlite.row_factory = aiosqlite.Row
            await self._sqlite.execute("PRAGMA foreign_keys = ON;")
            await self._sqlite.commit()
        await self._apply_schema()

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
        if self._sqlite is not None:
            await self._sqlite.close()

    async def _apply_schema(self) -> None:
        fname = "schema.sql" if self.engine == "postgres" else "schema_sqlite.sql"
        with open(os.path.join(SCHEMA_DIR, fname), "r", encoding="utf-8") as fh:
            script = fh.read()
        if self.engine == "postgres":
            async with self._pool.acquire() as conn:
                await conn.execute(script)
        else:
            await self._sqlite.executescript(script)
            await self._sqlite.commit()

    # ---- low-level helpers --------------------------------------------
    async def _execute(self, sql: str, params: Sequence[Any] = ()) -> None:
        if self.engine == "postgres":
            async with self._pool.acquire() as conn:
                await conn.execute(_pg(sql), *params)
        else:
            await self._sqlite.execute(sql, params)
            await self._sqlite.commit()

    async def _fetchone(self, sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        if self.engine == "postgres":
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(_pg(sql), *params)
                return dict(row) if row else None
        cur = await self._sqlite.execute(sql, params)
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def _fetchall(self, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        if self.engine == "postgres":
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(_pg(sql), *params)
                return [dict(r) for r in rows]
        cur = await self._sqlite.execute(sql, params)
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    # ---- giveaways -----------------------------------------------------
    async def create_giveaway(
        self,
        *,
        chat_id: int,
        creator_id: int,
        prize: str,
        description: str,
        winners_count: int,
        points_per_ref: int,
        required_channel: Optional[str],
        seed: str,
        ends_at: datetime,
    ) -> int:
        ends_val = ends_at.astimezone(timezone.utc)
        if self.engine == "postgres":
            row = await self._fetchone(
                """INSERT INTO giveaways
                   (chat_id, creator_id, prize, description, winners_count,
                    points_per_ref, required_channel, seed, ends_at)
                   VALUES (?,?,?,?,?,?,?,?,?) RETURNING id""",
                (chat_id, creator_id, prize, description, winners_count,
                 points_per_ref, required_channel, seed, ends_val),
            )
            return int(row["id"])
        cur = await self._sqlite.execute(
            """INSERT INTO giveaways
               (chat_id, creator_id, prize, description, winners_count,
                points_per_ref, required_channel, seed, ends_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (chat_id, creator_id, prize, description, winners_count,
             points_per_ref, required_channel, seed, ends_val.isoformat()),
        )
        await self._sqlite.commit()
        return int(cur.lastrowid)

    async def get_giveaway(self, giveaway_id: int) -> Optional[Dict[str, Any]]:
        return await self._fetchone("SELECT * FROM giveaways WHERE id = ?", (giveaway_id,))

    async def set_announce_msg(self, giveaway_id: int, msg_id: int) -> None:
        await self._execute(
            "UPDATE giveaways SET announce_msg_id = ? WHERE id = ?", (msg_id, giveaway_id)
        )

    async def latest_active_giveaway(self, chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if chat_id is not None:
            return await self._fetchone(
                "SELECT * FROM giveaways WHERE status='active' AND chat_id=? "
                "ORDER BY id DESC LIMIT 1",
                (chat_id,),
            )
        return await self._fetchone(
            "SELECT * FROM giveaways WHERE status='active' ORDER BY id DESC LIMIT 1"
        )

    async def due_giveaways(self) -> List[Dict[str, Any]]:
        """Active giveaways whose end time has passed."""
        now = _now_utc()
        if self.engine == "postgres":
            return await self._fetchall(
                "SELECT * FROM giveaways WHERE status='active' AND ends_at <= ?", (now,)
            )
        return await self._fetchall(
            "SELECT * FROM giveaways WHERE status='active' AND ends_at <= ?",
            (now.isoformat(),),
        )

    async def finish_giveaway(self, giveaway_id: int, winners: List[int]) -> None:
        finished = _now_utc()
        finished_val = finished if self.engine == "postgres" else finished.isoformat()
        await self._execute(
            "UPDATE giveaways SET status='finished', winners=?, finished_at=? WHERE id=?",
            (json.dumps(winners), finished_val, giveaway_id),
        )

    # ---- participants --------------------------------------------------
    async def add_participant(
        self, giveaway_id: int, user_id: int, username: Optional[str], full_name: Optional[str]
    ) -> bool:
        """Return True if newly added, False if already participating (dup)."""
        existing = await self._fetchone(
            "SELECT id FROM participants WHERE giveaway_id=? AND user_id=?",
            (giveaway_id, user_id),
        )
        if existing:
            return False
        try:
            await self._execute(
                "INSERT INTO participants (giveaway_id, user_id, username, full_name) "
                "VALUES (?,?,?,?)",
                (giveaway_id, user_id, username, full_name),
            )
        except Exception:
            # UNIQUE race -> treat as duplicate.
            return False
        return True

    async def is_participant(self, giveaway_id: int, user_id: int) -> bool:
        row = await self._fetchone(
            "SELECT 1 AS x FROM participants WHERE giveaway_id=? AND user_id=?",
            (giveaway_id, user_id),
        )
        return row is not None

    async def list_participants(self, giveaway_id: int) -> List[Dict[str, Any]]:
        return await self._fetchall(
            "SELECT * FROM participants WHERE giveaway_id=? ORDER BY user_id", (giveaway_id,)
        )

    async def count_participants(self, giveaway_id: int) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS c FROM participants WHERE giveaway_id=?", (giveaway_id,)
        )
        return int(row["c"]) if row else 0

    # ---- referrals -----------------------------------------------------
    async def add_referral(self, giveaway_id: int, inviter_id: int, invited_id: int) -> bool:
        """Credit a referral. Idempotent per invited_id; ignores self-invite."""
        if inviter_id == invited_id:
            return False
        existing = await self._fetchone(
            "SELECT id FROM referrals WHERE giveaway_id=? AND invited_id=?",
            (giveaway_id, invited_id),
        )
        if existing:
            return False
        try:
            await self._execute(
                "INSERT INTO referrals (giveaway_id, inviter_id, invited_id) VALUES (?,?,?)",
                (giveaway_id, inviter_id, invited_id),
            )
        except Exception:
            return False
        return True

    async def count_referrals(self, giveaway_id: int, inviter_id: int) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS c FROM referrals WHERE giveaway_id=? AND inviter_id=?",
            (giveaway_id, inviter_id),
        )
        return int(row["c"]) if row else 0

    async def count_all_referrals(self, giveaway_id: int) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS c FROM referrals WHERE giveaway_id=?", (giveaway_id,)
        )
        return int(row["c"]) if row else 0

    async def participants_with_tickets(
        self, giveaway_id: int, points_per_ref: int
    ) -> List[tuple]:
        """Return ``(user_id, tickets)`` for every participant of a giveaway."""
        rows = await self._fetchall(
            """SELECT p.user_id AS user_id,
                      (SELECT COUNT(*) FROM referrals r
                        WHERE r.giveaway_id = p.giveaway_id
                          AND r.inviter_id = p.user_id) AS refs
                 FROM participants p
                WHERE p.giveaway_id = ?
                ORDER BY p.user_id""",
            (giveaway_id,),
        )
        result = []
        for row in rows:
            refs = int(row["refs"] or 0)
            tickets = max(1, 1 + refs * points_per_ref)
            result.append((int(row["user_id"]), tickets))
        return result
