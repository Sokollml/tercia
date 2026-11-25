"""Tests for the pure rate-limiter core (app.middlewares.RateLimiter)."""
from __future__ import annotations

from app.middlewares import RateLimiter


def test_allows_up_to_limit_then_blocks():
    rl = RateLimiter(limit=3, window=10)
    # A controlled clock so the test is deterministic.
    t = 100.0
    assert rl.allow(1, now=t) is True
    assert rl.allow(1, now=t) is True
    assert rl.allow(1, now=t) is True
    assert rl.allow(1, now=t) is False  # 4th within the window


def test_window_slides_and_frees_capacity():
    rl = RateLimiter(limit=2, window=5)
    assert rl.allow(1, now=0.0) is True
    assert rl.allow(1, now=1.0) is True
    assert rl.allow(1, now=2.0) is False
    # After the window passes, capacity returns.
    assert rl.allow(1, now=7.0) is True


def test_limiter_is_per_key():
    rl = RateLimiter(limit=1, window=10)
    assert rl.allow(1, now=0.0) is True
    assert rl.allow(2, now=0.0) is True  # different user, own bucket
    assert rl.allow(1, now=0.0) is False


def test_minimum_limit_is_one():
    rl = RateLimiter(limit=0, window=10)  # coerced up to 1
    assert rl.allow(1, now=0.0) is True
    assert rl.allow(1, now=0.0) is False
