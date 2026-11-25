"""aiogram middlewares: per-user rate limiting for commands.

The throttle is intentionally tiny and in-memory: community quiz bots do not
need Redis just to stop a user from spamming ``/leaderboard``. Only messages
that look like commands are throttled, so poll answers and normal chatter are
never blocked.
"""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict, MutableMapping

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from .i18n import t


class ThrottlingMiddleware(BaseMiddleware):
    """Reject a user's commands that arrive faster than ``rate_limit_seconds``."""

    def __init__(self, rate_limit_seconds: float = 1.0) -> None:
        super().__init__()
        self.rate = max(0.0, float(rate_limit_seconds))
        self._last_seen: MutableMapping[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if self.rate <= 0 or not isinstance(event, Message):
            return await handler(event, data)

        text = event.text or ""
        if not text.startswith("/"):
            return await handler(event, data)

        user = event.from_user
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_seen.get(user.id)
        if last is not None and (now - last) < self.rate:
            lang = (user.language_code or "ru")[:2]
            try:
                await event.answer(t("rate_limited", lang))
            except Exception:  # pragma: no cover - best-effort notice
                pass
            return None

        self._last_seen[user.id] = now
        return await handler(event, data)
