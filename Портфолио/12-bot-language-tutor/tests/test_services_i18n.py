"""Tests for pure time helpers (app.services) and the i18n catalogue."""
from __future__ import annotations

from datetime import datetime, timezone

from app import services
from app.i18n import error_type_label, normalise_ui_lang, t


def test_now_ts_is_int_and_close_to_utc_now():
    ts = services.now_ts()
    assert isinstance(ts, int)
    delta = abs(ts - int(datetime.now(tz=timezone.utc).timestamp()))
    assert delta < 5


def test_today_str_format():
    # 2026-08-02 12:00 UTC
    ts = int(datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc).timestamp())
    assert services.today_str("UTC", ts) == "2026-08-02"


def test_today_str_respects_timezone_rollover():
    # 23:30 UTC on Aug 2 is already Aug 3 in Moscow (UTC+3).
    ts = int(datetime(2026, 8, 2, 23, 30, tzinfo=timezone.utc).timestamp())
    assert services.today_str("UTC", ts) == "2026-08-02"
    assert services.today_str("Europe/Moscow", ts) == "2026-08-03"


def test_to_local_and_format_when():
    ts = int(datetime(2026, 8, 2, 9, 5, tzinfo=timezone.utc).timestamp())
    assert services.format_when(ts, "UTC") == "02.08 09:05"


def test_bad_timezone_falls_back_to_utc():
    ts = int(datetime(2026, 8, 2, 9, 5, tzinfo=timezone.utc).timestamp())
    # Should not raise, just behave as UTC.
    assert services.format_when(ts, "Not/AZone") == "02.08 09:05"


def test_i18n_translation_and_formatting():
    assert t("cancelled", "ru")
    assert t("cancelled", "en") != t("cancelled", "ru")
    msg = t("quota_reached", "en", limit=30)
    assert "30" in msg


def test_i18n_defaults_and_fallbacks():
    assert normalise_ui_lang("fr") == "ru"  # unsupported -> default
    assert normalise_ui_lang("EN") == "en"
    # Missing key returns the key itself, never raises.
    assert t("no_such_key", "ru") == "no_such_key"


def test_error_type_label():
    assert error_type_label("tense", "ru") == "времена"
    assert error_type_label("tense", "en") == "tenses"
    assert error_type_label("weird_unknown", "ru")  # falls back to "other"
