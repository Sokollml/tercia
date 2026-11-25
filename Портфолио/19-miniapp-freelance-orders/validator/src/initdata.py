"""Валидация Telegram WebApp initData (HMAC-SHA256).

Эталонная реализация проверки подписи, которую Telegram кладёт в initData
мини-аппа. Та же логика продублирована в Code-ноде workflows/api.json (JS),
а здесь — на Python, чтобы покрыть тестами.

Алгоритм (docs: Telegram WebApps > Validating data):
  1. Разобрать initData как query-string в пары ключ=значение.
  2. Вынуть поле `hash`.
  3. data_check_string = "\n".join(f"{k}={v}") по остальным ключам,
     отсортированным по алфавиту.
  4. secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
  5. calc_hash = HMAC_SHA256(key=secret_key, msg=data_check_string).hex()
  6. Сравнить calc_hash с hash (constant-time).
  7. Проверить свежесть auth_date (защита от replay).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl


@dataclass
class InitDataResult:
    ok: bool
    reason: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    fields: Dict[str, str] = field(default_factory=dict)

    @property
    def user_id(self) -> Optional[int]:
        if self.user and "id" in self.user:
            try:
                return int(self.user["id"])
            except (TypeError, ValueError):
                return None
        return None


def _secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()


def _calc_hash(data_check_string: str, bot_token: str) -> str:
    return hmac.new(
        _secret_key(bot_token),
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def validate_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: Optional[int] = 86400,
    now: Optional[int] = None,
) -> InitDataResult:
    """Проверить подпись initData. Вернуть InitDataResult.

    max_age_seconds=None -> не проверять возраст auth_date.
    """
    if not init_data or not bot_token:
        return InitDataResult(ok=False, reason="empty_input")

    # keep_blank_values — чтобы порядок/наличие полей не терялись.
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return InitDataResult(ok=False, reason="no_hash")

    data_check_string = "\n".join(
        f"{k}={pairs[k]}" for k in sorted(pairs.keys())
    )
    calc = _calc_hash(data_check_string, bot_token)

    if not hmac.compare_digest(calc, received_hash):
        return InitDataResult(ok=False, reason="bad_hash", fields=pairs)

    # Возраст auth_date.
    if max_age_seconds is not None:
        auth_date_raw = pairs.get("auth_date")
        if not auth_date_raw:
            return InitDataResult(ok=False, reason="no_auth_date", fields=pairs)
        try:
            auth_date = int(auth_date_raw)
        except ValueError:
            return InitDataResult(ok=False, reason="bad_auth_date", fields=pairs)
        current = int(now if now is not None else time.time())
        if current - auth_date > max_age_seconds:
            return InitDataResult(ok=False, reason="expired", fields=pairs)

    user = None
    if "user" in pairs:
        try:
            user = json.loads(pairs["user"])
        except json.JSONDecodeError:
            user = None

    return InitDataResult(ok=True, user=user, fields=pairs)


def sign_init_data(fields: Dict[str, str], bot_token: str) -> str:
    """Собрать валидный initData из полей (для тестов/локальной отладки).

    НЕ для прода — только чтобы генерировать корректно подписанные данные.
    """
    data_check_string = "\n".join(
        f"{k}={fields[k]}" for k in sorted(fields.keys())
    )
    calc = _calc_hash(data_check_string, bot_token)
    from urllib.parse import urlencode

    payload = dict(fields)
    payload["hash"] = calc
    return urlencode(payload)
