"""Парсинг ответа ИИ-классификатора + fallback.

Эта логика — эталонная копия того, что делает Code-нода в
workflows/classify.json. Держим её тут отдельным модулем, чтобы покрыть
тестами на Python (n8n Code-нода на JS повторяет ту же схему).

ИИ иногда возвращает JSON, обёрнутый в ```json ... ``` или с мусором
до/после. Достаём объект, валидируем поля, приводим типы, подставляем
безопасные значения по умолчанию.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

VALID_URGENCY = {"low", "medium", "high"}

DEFAULT_RESULT: Dict[str, Any] = {
    "is_order": False,
    "service_type": None,
    "summary": None,
    "budget": None,
    "urgency": "low",
    "languages": [],
    "skills_required": [],
}


def _extract_json_blob(raw: str) -> Optional[str]:
    """Вытащить первый {...} блок из строки (снимая markdown-обёртку)."""
    if not raw:
        return None
    # снять ```json ... ``` или ``` ... ```
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if fenced:
        return fenced.group(1)
    # иначе — первый сбалансированный по грубому счёту объект
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]
    return None


def _to_float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        digits = re.sub(r"[^\d.]", "", value.replace(",", "."))
        if digits in ("", "."):
            return None
        try:
            return float(digits)
        except ValueError:
            return None
    return None


def _to_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip().lower()]
    return []


def parse_classifier_output(raw: str) -> Dict[str, Any]:
    """Разобрать сырой ответ ИИ в нормализованный dict.

    Никогда не бросает исключение: при любой ошибке возвращает DEFAULT_RESULT
    (is_order=False), чтобы пайплайн не падал на кривом ответе модели.
    """
    result = dict(DEFAULT_RESULT)

    blob = _extract_json_blob(raw)
    if blob is None:
        return result

    try:
        data = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        return result

    if not isinstance(data, dict):
        return result

    result["is_order"] = bool(data.get("is_order", False))

    service_type = data.get("service_type")
    result["service_type"] = (
        str(service_type).strip()
        if service_type not in (None, "", "null")
        else None
    )

    summary = data.get("summary")
    result["summary"] = (
        str(summary).strip() if summary not in (None, "", "null") else None
    )

    result["budget"] = _to_float_or_none(data.get("budget"))

    urgency = str(data.get("urgency", "low")).strip().lower()
    result["urgency"] = urgency if urgency in VALID_URGENCY else "low"

    langs = _to_str_list(data.get("languages"))
    result["languages"] = langs if langs else []

    result["skills_required"] = _to_str_list(data.get("skills_required"))

    return result
