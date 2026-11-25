"""Data-access layer: all SQL lives here, driver-agnostic.

Returns plain dicts, keeping handlers and tests free of SQL.  The spaced-
repetition maths lives in :mod:`app.srs`; this layer only persists its output.
Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import srs
from .db import Database


class Repository:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ---- users -----------------------------------------------------------
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM users WHERE id = ?", user_id)

    async def ensure_user(
        self, user_id: int, ui_lang: str, created_at: int
    ) -> Dict[str, Any]:
        """Fetch the user, creating a bare row on first contact."""
        row = await self.get_user(user_id)
        if row is None:
            await self.db.execute(
                "INSERT INTO users (id, ui_lang, created_at) VALUES (?, ?, ?)",
                user_id,
                ui_lang,
                created_at,
            )
            row = await self.get_user(user_id)
        assert row is not None
        return row

    async def set_ui_lang(self, user_id: int, ui_lang: str) -> None:
        await self.db.execute(
            "UPDATE users SET ui_lang = ? WHERE id = ?", ui_lang, user_id
        )

    async def set_learn_lang(self, user_id: int, learn_lang: str) -> None:
        await self.db.execute(
            "UPDATE users SET learn_lang = ? WHERE id = ?", learn_lang, user_id
        )

    async def set_level(self, user_id: int, level: str) -> None:
        await self.db.execute("UPDATE users SET level = ? WHERE id = ?", level, user_id)

    # ---- daily free-tier limit ------------------------------------------
    async def check_and_consume_quota(
        self, user_id: int, today: str, limit: int
    ) -> bool:
        """Consume one daily correction credit.

        Resets the per-user counter when the stored date rolls over.  Premium
        users are never limited.  Returns ``True`` when the action is allowed
        (and a credit was consumed), ``False`` when the free daily cap is hit.
        """
        row = await self.get_user(user_id)
        if row is None:
            return False
        if row.get("is_premium"):
            return True

        count = int(row.get("daily_count") or 0)
        if row.get("daily_date") != today:
            count = 0  # new day → reset

        if count >= limit:
            # Persist the (possibly reset) date so the row is consistent.
            await self.db.execute(
                "UPDATE users SET daily_date = ?, daily_count = ? WHERE id = ?",
                today,
                count,
                user_id,
            )
            return False

        await self.db.execute(
            "UPDATE users SET daily_date = ?, daily_count = ? WHERE id = ?",
            today,
            count + 1,
            user_id,
        )
        return True

    async def remaining_quota(self, user_id: int, today: str, limit: int) -> int:
        row = await self.get_user(user_id)
        if row is None:
            return 0
        if row.get("is_premium"):
            return limit  # effectively unlimited display
        if row.get("daily_date") != today:
            return limit
        return max(0, limit - int(row.get("daily_count") or 0))

    # ---- mistakes --------------------------------------------------------
    async def add_mistake(
        self,
        user_id: int,
        original: str,
        corrected: str,
        explanation: str,
        error_type: str,
        now_ts: int,
    ) -> int:
        next_review = srs.initial_next_review(now_ts)
        return await self.db.insert(
            "INSERT INTO mistakes "
            "(user_id, original, corrected, explanation, error_type, "
            " repetitions, interval_days, ease, next_review, created_at) "
            "VALUES (?, ?, ?, ?, ?, 0, 0, 2.5, ?, ?) RETURNING id",
            user_id,
            original,
            corrected,
            explanation,
            error_type,
            next_review,
            now_ts,
        )

    async def get_mistake(self, mistake_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM mistakes WHERE id = ?", mistake_id)

    async def count_mistakes(self, user_id: int) -> int:
        row = await self.db.fetchone(
            "SELECT COUNT(*) AS n FROM mistakes WHERE user_id = ?", user_id
        )
        return int(row["n"]) if row else 0

    async def due_mistakes(
        self, user_id: int, now_ts: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Mistakes whose ``next_review`` has arrived, soonest first."""
        return await self.db.fetchall(
            "SELECT * FROM mistakes "
            "WHERE user_id = ? AND next_review <= ? "
            "ORDER BY next_review ASC LIMIT ?",
            user_id,
            now_ts,
            limit,
        )

    async def count_due(self, user_id: int, now_ts: int) -> int:
        row = await self.db.fetchone(
            "SELECT COUNT(*) AS n FROM mistakes WHERE user_id = ? AND next_review <= ?",
            user_id,
            now_ts,
        )
        return int(row["n"]) if row else 0

    async def apply_review(
        self, mistake_id: int, success: bool, now_ts: int
    ) -> Optional[Dict[str, Any]]:
        """Update a mistake's SRS state after a quiz answer.

        Returns the updated row, or ``None`` if the mistake vanished.
        """
        row = await self.get_mistake(mistake_id)
        if row is None:
            return None

        updated = srs.schedule(
            repetitions=int(row.get("repetitions") or 0),
            interval_days=int(row.get("interval_days") or 0),
            ease=float(row.get("ease") or srs.DEFAULT_EASE),
            success=success,
            now_ts=now_ts,
        )
        correct_inc = 1 if success else 0
        wrong_inc = 0 if success else 1
        await self.db.execute(
            "UPDATE mistakes SET "
            "repetitions = ?, interval_days = ?, ease = ?, next_review = ?, "
            "times_correct = times_correct + ?, times_wrong = times_wrong + ?, "
            "last_reviewed = ? WHERE id = ?",
            updated["repetitions"],
            updated["interval_days"],
            updated["ease"],
            updated["next_review"],
            correct_inc,
            wrong_inc,
            now_ts,
            mistake_id,
        )
        return await self.get_mistake(mistake_id)

    async def top_error_types(
        self, user_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT error_type, COUNT(*) AS n FROM mistakes "
            "WHERE user_id = ? GROUP BY error_type ORDER BY n DESC LIMIT ?",
            user_id,
            limit,
        )

    # ---- sessions --------------------------------------------------------
    async def start_session(self, user_id: int, mode: str, now_ts: int) -> int:
        return await self.db.insert(
            "INSERT INTO sessions (user_id, mode, messages, started_at) "
            "VALUES (?, ?, 0, ?) RETURNING id",
            user_id,
            mode,
            now_ts,
        )

    async def bump_session(self, session_id: int) -> None:
        await self.db.execute(
            "UPDATE sessions SET messages = messages + 1 WHERE id = ?", session_id
        )

    async def end_session(self, session_id: int, now_ts: int) -> None:
        await self.db.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ? AND ended_at IS NULL",
            now_ts,
            session_id,
        )
