"""Pure business-logic helpers (no I/O), easy to unit-test.

Handles time math for slots and reminders.  Timestamps are UNIX epoch seconds
in UTC; formatting into a timezone is done here for display.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

try:  # zoneinfo is stdlib on 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]

REMINDER_LEAD_SECONDS = 3600  # remind one hour before the appointment


def now_ts() -> int:
    """Current UNIX time in seconds (UTC)."""
    return int(datetime.now(tz=timezone.utc).timestamp())


def reminder_ts(slot_start_ts: int, lead_seconds: int = REMINDER_LEAD_SECONDS) -> int:
    """Epoch at which the reminder for a slot should fire (start - lead)."""
    return slot_start_ts - lead_seconds


def should_schedule_reminder(
    slot_start_ts: int, current_ts: Optional[int] = None, lead_seconds: int = REMINDER_LEAD_SECONDS
) -> bool:
    """A reminder is worth scheduling only if its fire time is still in the future."""
    if current_ts is None:
        current_ts = now_ts()
    return reminder_ts(slot_start_ts, lead_seconds) > current_ts


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


def format_when(ts: int, tz_name: str) -> str:
    """Human friendly 'DD.MM HH:MM' rendering in the given timezone."""
    return to_local(ts, tz_name).strftime("%d.%m %H:%M")


def format_day(ts: int, tz_name: str) -> str:
    return to_local(ts, tz_name).strftime("%d.%m.%Y")


def parse_slot_input(raw: str, tz_name: str) -> Optional[int]:
    """Parse master input 'YYYY-MM-DD HH:MM' (local tz) to an epoch, or None."""
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H.%M", "%d.%m.%Y %H:%M"):
        try:
            naive = datetime.strptime(raw, fmt)
        except ValueError:
            continue
        aware = naive.replace(tzinfo=_tz(tz_name))
        return int(aware.timestamp())
    return None


def day_bounds(ts: int, tz_name: str) -> tuple:
    """Return (start_of_day_ts, start_of_next_day_ts) for the day containing ts."""
    local = to_local(ts, tz_name)
    start = local.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())
