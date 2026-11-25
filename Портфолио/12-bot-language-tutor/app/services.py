"""Pure time helpers (no I/O), easy to unit-test.

Timestamps are UNIX epoch seconds in UTC; timezone conversion is done only for
display and for computing the learner's "today" (which drives the daily quota
reset).  Compatible with Python 3.9.
"""
from __future__ import annotations

from datetime import datetime, timezone

try:  # zoneinfo is stdlib on 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


def now_ts() -> int:
    """Current UNIX time in seconds (UTC)."""
    return int(datetime.now(tz=timezone.utc).timestamp())


def _tz(tz_name: str):
    if ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return timezone.utc


def to_local(ts: int, tz_name: str) -> datetime:
    """Convert an epoch to a timezone-aware datetime in ``tz_name``."""
    return datetime.fromtimestamp(ts, tz=_tz(tz_name))


def today_str(tz_name: str, ts: int = None) -> str:  # type: ignore[assignment]
    """Return the learner's local calendar day as ``YYYY-MM-DD``."""
    if ts is None:
        ts = now_ts()
    return to_local(ts, tz_name).strftime("%Y-%m-%d")


def format_when(ts: int, tz_name: str) -> str:
    """Human friendly 'DD.MM HH:MM' rendering in the given timezone."""
    return to_local(ts, tz_name).strftime("%d.%m %H:%M")
