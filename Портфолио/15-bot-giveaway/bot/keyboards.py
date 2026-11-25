"""Inline keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import i18n


def participate_kb(giveaway_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t(lang, "btn_participate"),
                    callback_data=f"join:{giveaway_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t(lang, "btn_my_ticket"),
                    callback_data=f"reflink:{giveaway_id}",
                )
            ],
        ]
    )
