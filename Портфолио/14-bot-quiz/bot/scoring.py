"""Pure scoring logic — no I/O, easy to unit test."""
from __future__ import annotations

from typing import Optional


def calculate_points(
    is_correct: bool,
    *,
    base_points: int = 10,
    elapsed_seconds: Optional[float] = None,
    speed_window_seconds: int = 0,
    speed_bonus_max: int = 0,
) -> int:
    """Return points awarded for a single answer.

    * A wrong answer always scores ``0``.
    * A correct answer scores ``base_points`` plus an optional speed bonus.

    The speed bonus decays linearly from ``speed_bonus_max`` (answered
    instantly) down to ``0`` (answered at or after ``speed_window_seconds``).
    The bonus is only applied when both ``speed_bonus_max`` and
    ``speed_window_seconds`` are positive and ``elapsed_seconds`` is provided.
    """
    if not is_correct:
        return 0

    points = int(base_points)

    if (
        speed_bonus_max > 0
        and speed_window_seconds > 0
        and elapsed_seconds is not None
    ):
        elapsed = max(0.0, float(elapsed_seconds))
        remaining_fraction = max(0.0, 1.0 - (elapsed / float(speed_window_seconds)))
        points += int(round(speed_bonus_max * remaining_fraction))

    return points
