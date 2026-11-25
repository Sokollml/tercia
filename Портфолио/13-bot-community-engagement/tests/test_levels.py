"""Level / rank calculation from XP (pure logic, no DB)."""
from __future__ import annotations

from bot.xp import (
    LEVEL_BASE,
    level_for_xp,
    rank_for_level,
    xp_threshold,
    xp_to_next_level,
)


def test_zero_xp_is_level_zero():
    assert level_for_xp(0) == 0
    assert level_for_xp(-100) == 0


def test_thresholds_are_monotonic():
    prev = -1
    for lvl in range(0, 25):
        thr = xp_threshold(lvl)
        assert thr > prev
        prev = thr


def test_known_thresholds():
    # threshold(level) = 50 * level * (level+1) / 2
    assert xp_threshold(1) == 50
    assert xp_threshold(2) == 150
    assert xp_threshold(3) == 300


def test_level_boundaries():
    assert level_for_xp(49) == 0
    assert level_for_xp(50) == 1
    assert level_for_xp(149) == 1
    assert level_for_xp(150) == 2
    assert level_for_xp(299) == 2
    assert level_for_xp(300) == 3


def test_xp_to_next_level():
    assert xp_to_next_level(0) == 50
    assert xp_to_next_level(50) == 100   # next threshold 150
    assert xp_to_next_level(149) == 1


def test_rank_names():
    assert rank_for_level(0, "ru") == "Новичок"
    assert rank_for_level(0, "en") == "Newbie"
    assert rank_for_level(3, "en") == "Active"
    assert rank_for_level(100, "ru") == "Легенда"


def test_level_base_constant():
    assert LEVEL_BASE == 50
