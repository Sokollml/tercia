"""Тесты валидации Telegram initData (HMAC-SHA256)."""

import json
import time

import pytest

from initdata import sign_init_data, validate_init_data

BOT_TOKEN = "123456:TEST_BOT_TOKEN_abcdef"


def _fields(auth_date=None, user_id=42):
    return {
        "auth_date": str(auth_date if auth_date is not None else int(time.time())),
        "query_id": "AAA-test",
        "user": json.dumps({"id": user_id, "first_name": "Тест", "username": "t"}),
    }


def test_valid_signature_ok():
    init = sign_init_data(_fields(), BOT_TOKEN)
    res = validate_init_data(init, BOT_TOKEN)
    assert res.ok is True
    assert res.user_id == 42
    assert res.user["username"] == "t"


def test_tampered_field_fails():
    init = sign_init_data(_fields(user_id=1), BOT_TOKEN)
    # подменяем user после подписи
    tampered = init.replace("Тест", "Взлом") if "Тест" in init else init + "&x=1"
    res = validate_init_data(tampered, BOT_TOKEN)
    assert res.ok is False
    assert res.reason == "bad_hash"


def test_wrong_bot_token_fails():
    init = sign_init_data(_fields(), BOT_TOKEN)
    res = validate_init_data(init, "999:OTHER_TOKEN")
    assert res.ok is False
    assert res.reason == "bad_hash"


def test_missing_hash_fails():
    res = validate_init_data("auth_date=1&user=%7B%7D", BOT_TOKEN)
    assert res.ok is False
    assert res.reason == "no_hash"


def test_empty_input_fails():
    assert validate_init_data("", BOT_TOKEN).reason == "empty_input"
    assert validate_init_data("x=1&hash=y", "").reason == "empty_input"


def test_expired_auth_date():
    old = int(time.time()) - 100000
    init = sign_init_data(_fields(auth_date=old), BOT_TOKEN)
    res = validate_init_data(init, BOT_TOKEN, max_age_seconds=3600)
    assert res.ok is False
    assert res.reason == "expired"


def test_expired_ignored_when_max_age_none():
    old = int(time.time()) - 100000
    init = sign_init_data(_fields(auth_date=old), BOT_TOKEN)
    res = validate_init_data(init, BOT_TOKEN, max_age_seconds=None)
    assert res.ok is True


def test_fixed_now_within_window():
    init = sign_init_data(_fields(auth_date=1000), BOT_TOKEN)
    res = validate_init_data(init, BOT_TOKEN, max_age_seconds=100, now=1050)
    assert res.ok is True


def test_bad_auth_date_value():
    fields = _fields()
    fields["auth_date"] = "notanumber"
    init = sign_init_data(fields, BOT_TOKEN)
    res = validate_init_data(init, BOT_TOKEN)
    assert res.ok is False
    assert res.reason == "bad_auth_date"
