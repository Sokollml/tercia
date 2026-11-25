"""Middlewares: simple in-memory rate limiting and error shielding."""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Deque, Dict, MutableMapping

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from .texts import t

log = logging.getLogger("booking.mw")


class RateLimitMiddleware(BaseMiddleware):
    """Sliding-window limiter: at most ``limit`` events per ``window`` seconds
    per user.  Over-limit updates are dropped with a gentle notice."""

    def __init__(self, limit: int = 5, window: float = 3.0) -> None:
        self.limit = max(1, limit)
        self.window = max(0.5, window)
        self._hits: MutableMapping[int, Deque[float]] = defaultdict(deque)

    def _user_id(self, event: TelegramObject) -> int | None:
        user = getattr(event, "from_user", None)
        return user.id if user is not None else None

    def _allowed(self, user_id: int) -> bool:
        now = time.monotonic()
        hits = self._hits[user_id]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._user_id(event)
        if user_id is not None and not self._allowed(user_id):
            lang = data.get("lang", "ru")
            log.warning("rate limit hit for user %s", user_id)
            try:
                if isinstance(event, CallbackQuery):
                    await event.answer(t("rate_limited", lang), show_alert=False)
                elif isinstance(event, Message):
                    await event.answer(t("rate_limited", lang))
            except Exception:  # pragma: no cover - best effort notice
                pass
            return None
        return await handler(event, data)


class LangMiddleware(BaseMiddleware):
    """Injects the user's language into handler data.

    Language is resolved from an in-memory store (per user id) and defaults to
    the configured default.  Also injects the ``is_master`` flag and shared
    services (repository / config).
    """

    def __init__(
        self, default_lang: str, master_ids, repo, config, lang_store: Dict[int, str]
    ) -> None:
        self.default_lang = default_lang
        self.master_ids = set(master_ids)
        self.repo = repo
        self.config = config
        self.lang_store = lang_store

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        uid = user.id if user is not None else None
        data["lang"] = self.lang_store.get(uid, self.default_lang) if uid else self.default_lang
        data["is_master"] = uid in self.master_ids if uid else False
        data["repo"] = self.repo
        data["config"] = self.config
        data["lang_store"] = self.lang_store
        return await handler(event, data)
