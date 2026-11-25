"""Inline keyboards for the client and master flows."""
from __future__ import annotations

from typing import Any, Dict, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .services import format_when
from .texts import t


def main_menu(lang: str, is_master: bool) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t("menu_book", lang), callback_data="book")],
        [InlineKeyboardButton(text=t("menu_my", lang), callback_data="my")],
        [InlineKeyboardButton(text=t("menu_lang", lang), callback_data="lang")],
    ]
    if is_master:
        rows.append(
            [InlineKeyboardButton(text=t("menu_master", lang), callback_data="master")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def services_kb(services: List[Dict[str, Any]], lang: str) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    for sv in services:
        label = f"{sv['title']} · {sv['duration_min']} min · {sv['price']}"
        rows.append(
            [InlineKeyboardButton(text=label, callback_data=f"svc:{sv['id']}")]
        )
    rows.append([InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def slots_kb(slots: List[Dict[str, Any]], tz: str, lang: str) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for slot in slots:
        row.append(
            InlineKeyboardButton(
                text=format_when(slot["start_ts"], tz),
                callback_data=f"slot:{slot['id']}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="book")])
    rows.append([InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb(slot_id: int, service_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_confirm", lang),
                    callback_data=f"confirm:{slot_id}:{service_id}",
                )
            ],
            [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")],
        ]
    )


def my_bookings_kb(bookings: List[Dict[str, Any]], lang: str) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    for b in bookings:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{t('btn_cancel_booking', lang)} #{b['id']}",
                    callback_data=f"cxl:{b['id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def master_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_schedule", lang), callback_data="m_schedule")],
            [InlineKeyboardButton(text=t("btn_add_slot", lang), callback_data="m_addslot")],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="home")],
        ]
    )


def schedule_kb(
    bookings: List[Dict[str, Any]], free_slots: List[Dict[str, Any]], lang: str
) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    for b in bookings:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{t('btn_cancel_booking', lang)} #{b['id']}",
                    callback_data=f"m_cxl:{b['id']}",
                )
            ]
        )
    for s in free_slots:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{t('btn_close_slot', lang)} #{s['id']}",
                    callback_data=f"m_close:{s['id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="master")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang:en"),
            ]
        ]
    )
