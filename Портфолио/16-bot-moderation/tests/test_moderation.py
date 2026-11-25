"""Unit tests for the pure moderation logic (no I/O)."""
from __future__ import annotations

import random

from app.moderation import (
    FloodTracker,
    check_captcha,
    format_duration,
    has_link,
    is_expired,
    make_captcha,
    matched_stopword,
    parse_stopwords,
    should_mute,
)


def test_should_mute_threshold():
    assert should_mute(2, 3) is False
    assert should_mute(3, 3) is True
    assert should_mute(4, 3) is True


def test_should_mute_disabled_when_limit_zero():
    assert should_mute(10, 0) is False


def test_make_captcha_is_solvable_and_deterministic():
    rng = random.Random(42)
    cap = make_captcha(rng)
    assert cap.answer in cap.options
    assert len(cap.options) == 3
    assert check_captcha(cap.answer, cap.answer) is True
    assert check_captcha(cap.answer, "999") is False


def test_is_expired():
    assert is_expired(100, now=101) is True
    assert is_expired(100, now=100) is True
    assert is_expired(100, now=99) is False


def test_has_link():
    assert has_link("visit https://spam.example") is True
    assert has_link("join t.me/spamchannel") is True
    assert has_link("ping @spammerbotname") is True
    assert has_link("hello everyone") is False


def test_stopwords():
    words = parse_stopwords("spam, casino ,  ")
    assert words == ["spam", "casino"]
    assert matched_stopword("free CASINO here", words) == "casino"
    assert matched_stopword("nothing bad", words) is None


def test_flood_tracker_trips_over_limit():
    ft = FloodTracker(limit=3, window=10)
    now = 1000.0
    assert ft.hit(1, 7, now=now) is False
    assert ft.hit(1, 7, now=now) is False
    assert ft.hit(1, 7, now=now) is False
    # 4th message within the window trips the flood.
    assert ft.hit(1, 7, now=now) is True


def test_flood_tracker_window_slides():
    ft = FloodTracker(limit=2, window=5)
    assert ft.hit(1, 7, now=100.0) is False
    assert ft.hit(1, 7, now=100.0) is False
    # Later than the window -> old hits expire, not flooding.
    assert ft.hit(1, 7, now=200.0) is False


def test_format_duration():
    assert format_duration(0) == "∞"
    assert format_duration(3600, "ru") == "1ч"
    assert format_duration(90, "en") == "1m 30s"
