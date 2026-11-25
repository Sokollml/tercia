"""aiogram middlewares: dependency injection and per-user rate limiting.

The rate-limiter core (:class:`RateLimiter`) is a pure in-memory sliding-window
counter with no aiogram dependency, so it is unit-testable on its own.  The
middleware classes wrap it and inject shared services (repository, LLM client,
config) into every handler call.  Compatible with Python 3.9.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Deque, Dict, MutableMapping

try:
    from aiogram import BaseMiddleware
    from aiogram.types import TelegramObject
except Exception:  # pragma: no cover - import-safe without aiogram
    class BaseMiddleware:  # type: ignore[no-redef]
        pass

    TelegramObject = object  # type: ignore[assignment,misc]


class RateLimiter:
    """Sliding-window limiter: at most ``limit`` hits per ``window`` seconds."""

    def __init__(self, limit: int, window: float) -> None:
        self.limit = max(1, int(limit))
        self.window = float(window)
        self._hits: MutableMapping[int, Deque[float]] = defaultdict(deque)

    def allow(self, key: int, now: float = None) -> bool:  # type: ignore[assignment]
        """Return ``True`` if the action is allowed and record the hit."""
        if now is None:
            now = time.monotonic()
        bucket = self._hits[key]
        cutoff = now - self.window
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


class DependencyMiddleware(BaseMiddleware):
    """Inject shared services into every handler's ``data`` kwargs."""

    def __init__(self, **deps: Any) -> None:
        self._deps = deps

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        data.update(self._deps)
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Drop messages from a user who is sending them too fast."""

    def __init__(self, limiter: RateLimiter, ui_lang_default: str = "ru") -> None:
        self.limiter = limiter
        self.ui_lang_default = ui_lang_default

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is not None and not self.limiter.allow(user.id):
            # Silently swallow; optionally notify once.
            from .i18n import t

            answer = getattr(event, "answer", None)
            if callable(answer):
                try:
                    await answer(t("rate_limited", self.ui_lang_default))
                except Exception:  # pragma: no cover - best effort
                    pass
            return None
        return await handler(event, data)
