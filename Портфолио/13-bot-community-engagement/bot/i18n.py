"""Minimal RU/EN translation helper."""
from __future__ import annotations

from typing import Dict

STRINGS: Dict[str, Dict[str, str]] = {
    "welcome_default": {
        "ru": (
            "Привет, {name}! Добро пожаловать в чат.\n\n"
            "Правила простые: будь вежлив, без спама и рекламы.\n"
            "За активность начисляются очки — набирай XP и поднимайся в топе! /help"
        ),
        "en": (
            "Hi {name}! Welcome to the chat.\n\n"
            "Rules are simple: be polite, no spam or ads.\n"
            "You earn XP for activity — climb the leaderboard! /help"
        ),
    },
    "help": {
        "ru": (
            "<b>Команды:</b>\n"
            "/me — твоя карточка (очки, ранг, место)\n"
            "/top — топ за неделю и за всё время\n"
            "/rank — таблица рангов\n"
            "/help — эта справка\n\n"
            "<b>Админам:</b>\n"
            "/settings — текущие настройки чата\n"
            "/set &lt;параметр&gt; &lt;значение&gt; — изменить настройку\n"
            "/setwelcome &lt;текст&gt; — задать приветствие\n"
            "/toggle &lt;модуль&gt; — вкл/выкл модуль\n"
            "/prompt — задать вопрос дня прямо сейчас\n"
            "/lang ru|en — язык чата"
        ),
        "en": (
            "<b>Commands:</b>\n"
            "/me — your card (XP, rank, position)\n"
            "/top — weekly and all-time leaderboard\n"
            "/rank — ranks table\n"
            "/help — this help\n\n"
            "<b>Admins:</b>\n"
            "/settings — current chat settings\n"
            "/set &lt;key&gt; &lt;value&gt; — change a setting\n"
            "/setwelcome &lt;text&gt; — set welcome message\n"
            "/toggle &lt;module&gt; — enable/disable a module\n"
            "/prompt — post the question of the day now\n"
            "/lang ru|en — chat language"
        ),
    },
    "me_card": {
        "ru": (
            "<b>{name}</b>\n"
            "🏅 Ранг: {rank} (уровень {level})\n"
            "⭐ Очки: {xp} (до след. уровня: {to_next})\n"
            "🔥 Стрик: {streak} дн.\n"
            "📊 Место в чате: #{position}"
        ),
        "en": (
            "<b>{name}</b>\n"
            "🏅 Rank: {rank} (level {level})\n"
            "⭐ XP: {xp} (to next level: {to_next})\n"
            "🔥 Streak: {streak} days\n"
            "📊 Position: #{position}"
        ),
    },
    "top_header_week": {"ru": "🏆 <b>Топ за неделю</b>", "en": "🏆 <b>Weekly top</b>"},
    "top_header_all": {"ru": "👑 <b>Топ за всё время</b>", "en": "👑 <b>All-time top</b>"},
    "top_empty": {"ru": "Пока пусто — общайтесь, чтобы попасть в топ!", "en": "Empty for now — chat to get on the board!"},
    "weekly_congrats": {
        "ru": "🎉 Поздравляем лидеров недели! Спасибо, что оживляете чат.",
        "en": "🎉 Congrats to this week's leaders! Thanks for keeping the chat alive.",
    },
    "levelup": {
        "ru": "🎈 {name} повысил(а) уровень до <b>{level}</b> — ранг «{rank}»!",
        "en": "🎈 {name} reached level <b>{level}</b> — rank \"{rank}\"!",
    },
    "streak_badge": {
        "ru": "🔥 {name} держит стрик {streak} дней подряд! Бейдж активности разблокирован.",
        "en": "🔥 {name} is on a {streak}-day streak! Activity badge unlocked.",
    },
    "not_admin": {"ru": "Эта команда только для админов чата.", "en": "This command is for chat admins only."},
    "settings_saved": {"ru": "✅ Настройка сохранена.", "en": "✅ Setting saved."},
    "settings_bad": {"ru": "⚠️ Не понял параметр или значение. Смотри /help.", "en": "⚠️ Unknown key/value. See /help."},
    "welcome_set": {"ru": "✅ Приветствие обновлено.", "en": "✅ Welcome message updated."},
    "group_only": {"ru": "Команда работает только в группах.", "en": "This command works in groups only."},
    "ranks_table": {"ru": "<b>Ранги:</b>", "en": "<b>Ranks:</b>"},
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    lang = lang if lang in ("ru", "en") else "ru"
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("ru") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
