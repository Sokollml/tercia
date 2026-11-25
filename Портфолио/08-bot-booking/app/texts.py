"""Multilanguage text catalog (RU / EN).

Usage:
    from app.texts import t
    t("welcome", "ru", name="Anna")
"""
from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "ru"
SUPPORTED = ("ru", "en")

TEXTS: Dict[str, Dict[str, str]] = {
    "welcome": {
        "ru": "Привет, {name}! Я помогу записаться к мастеру.\nНажмите «Записаться», чтобы начать.",
        "en": "Hi, {name}! I'll help you book an appointment.\nTap “Book” to start.",
    },
    "welcome_master": {
        "ru": "Добро пожаловать, мастер {name}! Вам доступна панель управления.",
        "en": "Welcome, master {name}! The control panel is available to you.",
    },
    "menu_book": {"ru": "📅 Записаться", "en": "📅 Book"},
    "menu_my": {"ru": "🗒 Мои записи", "en": "🗒 My bookings"},
    "menu_lang": {"ru": "🌐 Язык", "en": "🌐 Language"},
    "menu_master": {"ru": "🛠 Панель мастера", "en": "🛠 Master panel"},
    "choose_service": {
        "ru": "Выберите услугу:",
        "en": "Choose a service:",
    },
    "no_services": {
        "ru": "Пока нет доступных услуг. Загляните позже.",
        "en": "No services available yet. Please check back later.",
    },
    "choose_slot": {
        "ru": "Услуга: {service}\nВыберите свободное время:",
        "en": "Service: {service}\nChoose an available time:",
    },
    "no_slots": {
        "ru": "Свободных слотов нет. Попробуйте позже.",
        "en": "No free slots. Please try again later.",
    },
    "confirm": {
        "ru": "Подтвердите запись:\n\n📌 Услуга: {service}\n🕒 Время: {when}\n💰 Цена: {price}\n\nВсё верно?",
        "en": "Please confirm:\n\n📌 Service: {service}\n🕒 Time: {when}\n💰 Price: {price}\n\nIs everything correct?",
    },
    "btn_confirm": {"ru": "✅ Подтвердить", "en": "✅ Confirm"},
    "btn_cancel": {"ru": "❌ Отмена", "en": "❌ Cancel"},
    "btn_back": {"ru": "⬅️ Назад", "en": "⬅️ Back"},
    "booked_ok": {
        "ru": "✅ Готово! Вы записаны на {when} — {service}.\nНапомним за час до визита.",
        "en": "✅ Done! You're booked for {when} — {service}.\nWe'll remind you an hour before.",
    },
    "slot_taken": {
        "ru": "😔 Увы, этот слот только что заняли. Выберите другое время.",
        "en": "😔 Sorry, this slot was just taken. Please pick another time.",
    },
    "cancelled": {"ru": "Действие отменено.", "en": "Action cancelled."},
    "reminder": {
        "ru": "⏰ Напоминание: через час у вас запись — {service} в {when}.",
        "en": "⏰ Reminder: you have an appointment in an hour — {service} at {when}.",
    },
    "my_empty": {
        "ru": "У вас пока нет активных записей.",
        "en": "You have no active bookings yet.",
    },
    "my_item": {
        "ru": "• {when} — {service} (№{id})",
        "en": "• {when} — {service} (#{id})",
    },
    "booking_cancelled": {
        "ru": "Запись №{id} отменена.",
        "en": "Booking #{id} cancelled.",
    },
    # Master panel
    "master_only": {
        "ru": "Эта команда доступна только мастеру.",
        "en": "This command is for the master only.",
    },
    "master_menu": {
        "ru": "Панель мастера. Выберите действие:",
        "en": "Master panel. Choose an action:",
    },
    "btn_schedule": {"ru": "📆 Расписание на день", "en": "📆 Day schedule"},
    "btn_add_slot": {"ru": "➕ Добавить слот", "en": "➕ Add slot"},
    "schedule_header": {
        "ru": "Расписание на {day}:",
        "en": "Schedule for {day}:",
    },
    "schedule_empty": {
        "ru": "На этот день записей и слотов нет.",
        "en": "No slots or bookings for this day.",
    },
    "schedule_line_booked": {
        "ru": "🔴 {when} — {service} (клиент {client}) №{id}",
        "en": "🔴 {when} — {service} (client {client}) #{id}",
    },
    "schedule_line_free": {
        "ru": "🟢 {when} — свободно",
        "en": "🟢 {when} — free",
    },
    "schedule_line_closed": {
        "ru": "⚪️ {when} — закрыто",
        "en": "⚪️ {when} — closed",
    },
    "btn_cancel_booking": {"ru": "Отменить запись", "en": "Cancel booking"},
    "btn_close_slot": {"ru": "Закрыть слот", "en": "Close slot"},
    "slot_closed_ok": {"ru": "Слот закрыт.", "en": "Slot closed."},
    "master_cancelled": {
        "ru": "Запись №{id} отменена, клиент уведомлён.",
        "en": "Booking #{id} cancelled, client notified.",
    },
    "client_notified_cancel": {
        "ru": "❗️ Ваша запись на {when} ({service}) была отменена мастером.",
        "en": "❗️ Your booking for {when} ({service}) was cancelled by the master.",
    },
    "add_slot_prompt": {
        "ru": "Введите дату и время слота в формате:\nГГГГ-ММ-ДД ЧЧ:ММ\nНапример: 2026-08-05 14:30",
        "en": "Enter slot date and time as:\nYYYY-MM-DD HH:MM\nExample: 2026-08-05 14:30",
    },
    "add_slot_bad": {
        "ru": "Не удалось разобрать дату. Формат: ГГГГ-ММ-ДД ЧЧ:ММ",
        "en": "Could not parse the date. Format: YYYY-MM-DD HH:MM",
    },
    "add_slot_past": {
        "ru": "Нельзя добавить слот в прошлом.",
        "en": "Cannot add a slot in the past.",
    },
    "add_slot_ok": {
        "ru": "Слот на {when} добавлен.",
        "en": "Slot for {when} added.",
    },
    "lang_choose": {"ru": "Выберите язык:", "en": "Choose language:"},
    "lang_set": {"ru": "Язык переключён на русский.", "en": "Language switched to English."},
    "error_generic": {
        "ru": "Что-то пошло не так. Попробуйте ещё раз.",
        "en": "Something went wrong. Please try again.",
    },
    "rate_limited": {
        "ru": "Слишком много запросов. Подождите пару секунд.",
        "en": "Too many requests. Please wait a couple of seconds.",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Return the localized string for ``key`` formatted with kwargs."""
    lang = lang if lang in SUPPORTED else DEFAULT_LANG
    entry = TEXTS.get(key)
    if entry is None:
        return key
    template = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
