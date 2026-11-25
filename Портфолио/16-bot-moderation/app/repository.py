"""Data-access layer over the driver-agnostic :class:`Database`.

Only this module knows the SQL; handlers deal in plain dicts / ints.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .config import Config
from .db import Database
from .moderation import now_ts


class Repository:
    def __init__(self, db: Database, cfg: Config) -> None:
        self.db = db
        self.cfg = cfg

    # ------------------------------------------------------------------ #
    # Chats / settings
    # ------------------------------------------------------------------ #
    async def get_chat(self, chat_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM chats WHERE chat_id = ?", chat_id)

    async def ensure_chat(self, chat_id: int, title: str = "") -> Dict[str, Any]:
        """Fetch a chat's settings, creating a default row on first sight."""
        row = await self.get_chat(chat_id)
        if row is not None:
            return row
        cfg = self.cfg
        await self.db.execute(
            "INSERT INTO chats (chat_id, title, lang, captcha_enabled, captcha_timeout, "
            "warn_limit, mute_duration, antiflood_limit, antiflood_window, created_at) "
            "VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)",
            chat_id,
            title,
            cfg.default_lang,
            cfg.captcha_timeout,
            cfg.warn_limit,
            cfg.mute_duration,
            cfg.antiflood_limit,
            cfg.antiflood_window,
            now_ts(),
        )
        row = await self.get_chat(chat_id)
        assert row is not None
        return row

    async def update_setting(self, chat_id: int, column: str, value: Any) -> None:
        """Update a single whitelisted settings column."""
        if column not in ALLOWED_SETTINGS:
            raise ValueError("unknown setting: %s" % column)
        await self.db.execute(
            "UPDATE chats SET %s = ? WHERE chat_id = ?" % column, value, chat_id
        )

    # ------------------------------------------------------------------ #
    # Warnings
    # ------------------------------------------------------------------ #
    async def add_warning(
        self, chat_id: int, user_id: int, admin_id: int, reason: str = ""
    ) -> int:
        return await self.db.insert(
            "INSERT INTO warnings (chat_id, user_id, admin_id, reason, active, created_at) "
            "VALUES (?, ?, ?, ?, 1, ?) RETURNING id",
            chat_id,
            user_id,
            admin_id,
            reason,
            now_ts(),
        )

    async def count_active_warnings(self, chat_id: int, user_id: int) -> int:
        row = await self.db.fetchone(
            "SELECT COUNT(*) AS n FROM warnings "
            "WHERE chat_id = ? AND user_id = ? AND active = 1",
            chat_id,
            user_id,
        )
        return int(row["n"]) if row else 0

    async def reset_warnings(self, chat_id: int, user_id: int) -> None:
        await self.db.execute(
            "UPDATE warnings SET active = 0 WHERE chat_id = ? AND user_id = ?",
            chat_id,
            user_id,
        )

    # ------------------------------------------------------------------ #
    # Mutes
    # ------------------------------------------------------------------ #
    async def add_mute(
        self,
        chat_id: int,
        user_id: int,
        until_ts: int,
        admin_id: int = 0,
        reason: str = "",
    ) -> int:
        # Deactivate any previous active mute for the same user first.
        await self.db.execute(
            "UPDATE mutes SET active = 0 WHERE chat_id = ? AND user_id = ? AND active = 1",
            chat_id,
            user_id,
        )
        return await self.db.insert(
            "INSERT INTO mutes (chat_id, user_id, admin_id, reason, until_ts, active, created_at) "
            "VALUES (?, ?, ?, ?, ?, 1, ?) RETURNING id",
            chat_id,
            user_id,
            admin_id,
            reason,
            until_ts,
            now_ts(),
        )

    async def deactivate_mute(self, chat_id: int, user_id: int) -> None:
        await self.db.execute(
            "UPDATE mutes SET active = 0 WHERE chat_id = ? AND user_id = ? AND active = 1",
            chat_id,
            user_id,
        )

    async def active_mute(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone(
            "SELECT * FROM mutes WHERE chat_id = ? AND user_id = ? AND active = 1 "
            "ORDER BY id DESC LIMIT 1",
            chat_id,
            user_id,
        )

    # ------------------------------------------------------------------ #
    # Captcha pending
    # ------------------------------------------------------------------ #
    async def add_pending(
        self, chat_id: int, user_id: int, message_id: int, answer: str, deadline_ts: int
    ) -> None:
        # Replace any stale pending row for the same (chat, user).
        await self.db.execute(
            "DELETE FROM captcha_pending WHERE chat_id = ? AND user_id = ?",
            chat_id,
            user_id,
        )
        await self.db.execute(
            "INSERT INTO captcha_pending (chat_id, user_id, message_id, answer, deadline_ts, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            chat_id,
            user_id,
            message_id,
            answer,
            deadline_ts,
            now_ts(),
        )

    async def get_pending(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone(
            "SELECT * FROM captcha_pending WHERE chat_id = ? AND user_id = ?",
            chat_id,
            user_id,
        )

    async def remove_pending(self, chat_id: int, user_id: int) -> None:
        await self.db.execute(
            "DELETE FROM captcha_pending WHERE chat_id = ? AND user_id = ?",
            chat_id,
            user_id,
        )

    async def due_pending(self, now: int) -> List[Dict[str, Any]]:
        """All pending captchas whose deadline has passed."""
        return await self.db.fetchall(
            "SELECT * FROM captcha_pending WHERE deadline_ts <= ?", now
        )

    # ------------------------------------------------------------------ #
    # Action log
    # ------------------------------------------------------------------ #
    async def log_action(
        self,
        chat_id: int,
        action: str,
        actor_id: int = 0,
        target_id: int = 0,
        details: str = "",
    ) -> None:
        await self.db.execute(
            "INSERT INTO action_log (chat_id, actor_id, target_id, action, details, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            chat_id,
            actor_id,
            target_id,
            action,
            details,
            now_ts(),
        )

    async def recent_actions(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT * FROM action_log WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
            chat_id,
            limit,
        )


# Columns an admin is allowed to change through /set. Keeps update_setting safe
# from SQL injection via the column name.
ALLOWED_SETTINGS = {
    "lang",
    "rules_text",
    "welcome_text",
    "captcha_enabled",
    "captcha_timeout",
    "filter_links",
    "filter_forwards",
    "filter_stopwords",
    "stopwords",
    "antiflood_enabled",
    "antiflood_limit",
    "antiflood_window",
    "warn_limit",
    "mute_duration",
}
