"""Pure XP / level / anti-abuse logic.

This module has NO aiogram / DB dependencies on purpose so it can be unit
tested in isolation and reused by handlers and the scheduler.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

# --- Level curve ------------------------------------------------------------
# Cumulative XP required to *reach* a given level:
#   threshold(level) = LEVEL_BASE * level * (level + 1) / 2
# level 1 -> 50, level 2 -> 150, level 3 -> 300, level 4 -> 500 ...
LEVEL_BASE = 50

# Rank names by level range. (min_level_inclusive, name_ru, name_en)
RANKS: List[Tuple[int, str, str]] = [
    (0, "Новичок", "Newbie"),
    (3, "Активный", "Active"),
    (7, "Знаток", "Regular"),
    (12, "Ветеран", "Veteran"),
    (20, "Легенда", "Legend"),
]


def xp_threshold(level: int) -> int:
    """Total XP needed to be *at* ``level``. Level 0 requires 0 XP."""
    if level <= 0:
        return 0
    return int(LEVEL_BASE * level * (level + 1) / 2)


def level_for_xp(xp: int) -> int:
    """Return the level for a given total XP amount."""
    if xp < 0:
        return 0
    level = 0
    while xp >= xp_threshold(level + 1):
        level += 1
    return level


def xp_to_next_level(xp: int) -> int:
    """XP remaining until the next level up."""
    current = level_for_xp(xp)
    return max(0, xp_threshold(current + 1) - xp)


def rank_for_level(level: int, lang: str = "ru") -> str:
    """Human readable rank name for a level."""
    name_ru, name_en = RANKS[0][1], RANKS[0][2]
    for min_level, ru, en in RANKS:
        if level >= min_level:
            name_ru, name_en = ru, en
    return name_ru if lang == "ru" else name_en


# --- Anti-abuse XP awarding -------------------------------------------------

@dataclass
class XpSettings:
    """Tunable anti-abuse parameters (per chat)."""

    xp_per_message: int = 5
    cooldown_sec: int = 60          # min seconds between two XP awards
    min_message_len: int = 3        # messages shorter than this give no XP
    antiflood_window_sec: int = 5   # ignore messages closer than this
    ignore_commands: bool = True
    ignore_stickers: bool = True


@dataclass
class XpDecision:
    awarded: bool
    xp: int
    reason: str  # "ok" | "cooldown" | "too_short" | "command" | "sticker" | "flood" | "disabled"


def evaluate_message(
    *,
    text: Optional[str],
    is_command: bool,
    is_sticker: bool,
    now: datetime,
    last_xp_at: Optional[datetime],
    settings: XpSettings,
    enabled: bool = True,
) -> XpDecision:
    """Decide whether an incoming message earns XP.

    This is the single source of truth for the anti-abuse rules:
      * XP module disabled            -> no XP
      * stickers / commands (ignored) -> no XP
      * message shorter than min len  -> no XP
      * inside antiflood window       -> no XP
      * inside cooldown since last XP -> no XP
    """
    if not enabled:
        return XpDecision(False, 0, "disabled")

    if is_sticker and settings.ignore_stickers:
        return XpDecision(False, 0, "sticker")

    if is_command and settings.ignore_commands:
        return XpDecision(False, 0, "command")

    normalized = (text or "").strip()
    if len(normalized) < settings.min_message_len:
        return XpDecision(False, 0, "too_short")

    if last_xp_at is not None:
        elapsed = (now - last_xp_at).total_seconds()
        # Antiflood is a hard, short window; cooldown is the longer gate.
        if elapsed < settings.antiflood_window_sec:
            return XpDecision(False, 0, "flood")
        if elapsed < settings.cooldown_sec:
            return XpDecision(False, 0, "cooldown")

    return XpDecision(True, settings.xp_per_message, "ok")


# --- Streaks ----------------------------------------------------------------

def compute_streak(
    *,
    last_active_date: Optional["datetime.date"],
    today: "datetime.date",
    current_streak: int,
) -> int:
    """Update a daily activity streak.

    * same day               -> unchanged
    * consecutive day (+1)   -> streak + 1
    * gap of 2+ days / first -> reset to 1
    """
    if last_active_date is None:
        return 1
    if last_active_date == today:
        return current_streak if current_streak > 0 else 1
    if today - last_active_date == timedelta(days=1):
        return current_streak + 1
    return 1
