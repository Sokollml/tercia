"""Unit tests for the pure scoring logic."""
from __future__ import annotations

from bot.scoring import calculate_points


def test_wrong_answer_scores_zero():
    assert calculate_points(False, base_points=10) == 0
    # even with a generous speed bonus configured, a wrong answer is worth 0
    assert (
        calculate_points(
            False,
            base_points=10,
            elapsed_seconds=0,
            speed_window_seconds=60,
            speed_bonus_max=5,
        )
        == 0
    )


def test_correct_answer_base_only():
    # No speed bonus configured -> just the base points.
    assert calculate_points(True, base_points=10) == 10


def test_speed_bonus_full_when_instant():
    # Answered instantly -> full speed bonus.
    assert (
        calculate_points(
            True,
            base_points=10,
            elapsed_seconds=0,
            speed_window_seconds=60,
            speed_bonus_max=5,
        )
        == 15
    )


def test_speed_bonus_decays_to_zero_at_window_end():
    assert (
        calculate_points(
            True,
            base_points=10,
            elapsed_seconds=60,
            speed_window_seconds=60,
            speed_bonus_max=5,
        )
        == 10
    )


def test_speed_bonus_is_linear_midway():
    # Halfway through the window -> half the bonus (rounded).
    assert (
        calculate_points(
            True,
            base_points=10,
            elapsed_seconds=30,
            speed_window_seconds=60,
            speed_bonus_max=4,
        )
        == 12
    )


def test_speed_bonus_never_negative_past_window():
    assert (
        calculate_points(
            True,
            base_points=10,
            elapsed_seconds=999,
            speed_window_seconds=60,
            speed_bonus_max=5,
        )
        == 10
    )


def test_negative_elapsed_clamped():
    # Clock skew producing negative elapsed should not exceed the max bonus.
    assert (
        calculate_points(
            True,
            base_points=10,
            elapsed_seconds=-5,
            speed_window_seconds=60,
            speed_bonus_max=5,
        )
        == 15
    )
