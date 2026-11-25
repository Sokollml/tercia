"""Inline-keyboard builders and a small callback-data protocol.

Callback payloads are plain ``"prefix:value"`` strings (kept well under
Telegram's 64-byte limit).  The builders return ``InlineKeyboardMarkup`` objects
but aiogram is imported lazily so this module is import-safe in tests.
Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import List, Tuple

from .config import LEARN_LANGUAGES, LEVELS
from .i18n import t

# Callback-data prefixes.
CB_UI_LANG = "ui"
CB_LEARN_LANG = "learn"
CB_LEVEL = "lvl"
CB_QUIZ_SHOW = "qshow"
CB_QUIZ_GRADE = "qgrade"


def _markup(rows: List[List[Tuple[str, str]]]):
    """Build an ``InlineKeyboardMarkup`` from ``[(text, callback_data)]`` rows."""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [
        [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
        for row in rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def ui_lang_keyboard():
    return _markup(
        [
            [
                ("🇷🇺 Русский", "{}:ru".format(CB_UI_LANG)),
                ("🇬🇧 English", "{}:en".format(CB_UI_LANG)),
            ]
        ]
    )


def learn_lang_keyboard(ui_lang: str):
    rows: List[List[Tuple[str, str]]] = []
    row: List[Tuple[str, str]] = []
    for code, names in LEARN_LANGUAGES.items():
        row.append((names.get(ui_lang, names["en"]), "{}:{}".format(CB_LEARN_LANG, code)))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return _markup(rows)


def level_keyboard():
    row = [("{}".format(lvl), "{}:{}".format(CB_LEVEL, lvl)) for lvl in LEVELS]
    return _markup([row])


def quiz_show_answer_keyboard(mistake_id: int, ui_lang: str):
    return _markup(
        [[(t("quiz_show_answer", ui_lang), "{}:{}".format(CB_QUIZ_SHOW, mistake_id))]]
    )


def quiz_grade_keyboard(mistake_id: int, ui_lang: str):
    return _markup(
        [
            [
                (t("quiz_grade_good", ui_lang), "{}:{}:1".format(CB_QUIZ_GRADE, mistake_id)),
                (t("quiz_grade_bad", ui_lang), "{}:{}:0".format(CB_QUIZ_GRADE, mistake_id)),
            ]
        ]
    )


def parse_callback(data: str) -> Tuple[str, List[str]]:
    """Split ``"prefix:a:b"`` into ``("prefix", ["a", "b"])``."""
    parts = (data or "").split(":")
    if not parts:
        return "", []
    return parts[0], parts[1:]
