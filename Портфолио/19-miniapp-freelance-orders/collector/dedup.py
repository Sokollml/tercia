"""Дедупликация сообщений по хешу нормализованного текста.

text_hash пишется в raw_messages.text_hash с UNIQUE-ограничением,
поэтому повторная вставка того же (по сути) текста отсекается на уровне БД.
Здесь — детерминированная нормализация + sha256, чтобы «одинаковые по смыслу»
перепосты давали одинаковый хеш.
"""

from __future__ import annotations

import hashlib
import re

# Убираем ссылки, @упоминания, эмодзи-подобные не-словесные символы,
# лишние пробелы и регистр — чтобы перепост с мелкими правками дедуплился.
_URL_RE = re.compile(r"https?://\S+|t\.me/\S+")
_MENTION_RE = re.compile(r"@\w+")
_NON_WORD_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize_for_hash(text: str) -> str:
    """Каноническая форма текста для хеширования."""
    if text is None:
        text = ""
    t = text.lower()
    t = _URL_RE.sub(" ", t)
    t = _MENTION_RE.sub(" ", t)
    t = _NON_WORD_RE.sub(" ", t)
    t = _SPACE_RE.sub(" ", t).strip()
    return t


def text_hash(text: str) -> str:
    """sha256 от нормализованного текста (hex)."""
    norm = normalize_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()
