"""Simple per-user rate limiting middleware (anti-spam)."""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict, MutableMapping

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """Drop events that arrive faster than ``rate`` seconds per user."""

    def __init__(self, rate: float = 0.7):
        self.rate = rate
        self._last: MutableMapping[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            now = time.monotonic()
            last = self._last.get(user.id, 0.0)
            if now - last < self.rate:
                # For button taps, answer quietly so the client stops spinning.
                if isinstance(event, CallbackQuery):
                    try:
                        await event.answer()
                    except Exception:
                        pass
                return None
            self._last[user.id] = now
        return await handler(event, data)
