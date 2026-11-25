"""Dispatcher middlewares: per-user rate limiting."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Deque, Dict, Tuple

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update


class ThrottlingMiddleware(BaseMiddleware):
    """Sliding-window rate limiter for incoming updates, keyed per user.

    Silently drops updates once a user exceeds ``limit`` events per ``window``
    seconds. This protects the bot (and DB) from abusive command spamming; it
    is independent of the per-chat antiflood moderation feature.
    """

    def __init__(self, limit: int = 5, window: float = 3.0) -> None:
        super().__init__()
        self.limit = max(1, limit)
        self.window = max(0.5, float(window))
        self._hits: Dict[int, Deque[float]] = defaultdict(deque)

    @staticmethod
    def _user_id(event: TelegramObject) -> int:
        user = getattr(event, "from_user", None)
        if user is None and isinstance(event, Update):
            ev = event.event
            user = getattr(ev, "from_user", None)
        return user.id if user is not None else 0

    def _is_flooding(self, user_id: int, now: float) -> bool:
        hits = self._hits[user_id]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        hits.append(now)
        return len(hits) > self.limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._user_id(event)
        if user_id and self._is_flooding(user_id, time.monotonic()):
            # Drop the update without answering to avoid amplifying the flood.
            return None
        return await handler(event, data)
