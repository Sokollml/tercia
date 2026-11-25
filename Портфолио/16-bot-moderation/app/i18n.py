"""Tiny RU/EN localization layer.

No external gettext machinery — a nested dict is more than enough for a bot
with a couple dozen strings, and it keeps the project dependency-free here.
"""
from __future__ import annotations

from typing import Any, Dict

DEFAULT_LANG = "ru"

# Editable-by-admin defaults (stored per chat, these are the fallbacks).
DEFAULT_RULES = {
    "ru": (
        "Правила сообщества:\n"
        "1. Уважайте участников.\n"
        "2. Без спама и рекламы.\n"
        "3. Оставайтесь в теме чата."
    ),
    "en": (
        "Community rules:\n"
        "1. Respect other members.\n"
        "2. No spam or advertising.\n"
        "3. Stay on topic."
    ),
}

DEFAULT_WELCOME = {
    "ru": "Добро пожаловать, {name}! Подтвердите, что вы не бот.",
    "en": "Welcome, {name}! Please prove you are not a bot.",
}

TEXTS: Dict[str, Dict[str, str]] = {
    "ru": {
        "start": (
            "Привет! Я бот-модератор для групп.\n"
            "Добавьте меня в группу и выдайте права администратора "
            "(бан, ограничение, удаление сообщений).\n"
            "Команды: /help"
        ),
        "help": (
            "Доступные команды:\n"
            "/rules — показать правила\n"
            "/warn — вынести предупреждение (ответом на сообщение)\n"
            "/mute [минуты] — заглушить пользователя\n"
            "/unmute — снять заглушку\n"
            "/ban — забанить пользователя\n"
            "/unban — разбанить (по id)\n"
            "/kick — удалить из чата\n"
            "/warns — счётчик предупреждений пользователя\n"
            "/log — последние действия модерации\n"
            "/settings — текущие настройки чата\n"
            "/set <параметр> <значение> — изменить настройку\n"
            "/setrules <текст> — задать правила\n"
            "/setwelcome <текст> — задать приветствие\n"
            "/lang <ru|en> — язык бота"
        ),
        "rules_not_set": "Правила пока не заданы. Администратор может задать их через /setrules.",
        "captcha_prompt": (
            "{name}, чтобы писать в чат, решите пример за {seconds} сек.:\n"
            "<b>{question}</b>"
        ),
        "captcha_pass": "Спасибо, {name}! Проверка пройдена.",
        "captcha_fail_wrong": "Неверный ответ. Доступ в чат закрыт.",
        "captcha_kick": "{name} не прошёл проверку и был удалён.",
        "captcha_not_yours": "Эта проверка не для вас.",
        "not_admin": "Команда доступна только администраторам.",
        "bot_not_admin": "Мне нужны права администратора (ограничение и бан участников).",
        "reply_required": "Ответьте этой командой на сообщение нарушителя.",
        "cant_target_admin": "Нельзя применить это действие к администратору.",
        "warn_issued": "⚠️ {name} получает предупреждение ({count}/{limit}). Причина: {reason}",
        "warn_muted": "🔇 {name} набрал {count} предупреждений и заглушён на {duration}.",
        "mute_issued": "🔇 {name} заглушён на {duration}. Причина: {reason}",
        "unmute_done": "🔊 {name} снова может писать.",
        "ban_issued": "⛔ {name} забанен. Причина: {reason}",
        "unban_done": "✅ Пользователь {user_id} разбанен.",
        "kick_done": "👢 {name} удалён из чата.",
        "spam_deleted": "🧹 Сообщение от {name} удалено ({reason}).",
        "flood_muted": "🔇 {name} заглушён на {duration} за флуд.",
        "warns_count": "У {name} активных предупреждений: {count}/{limit}.",
        "no_reason": "не указана",
        "settings_header": "⚙️ Настройки чата «{title}»:",
        "setting_updated": "✅ {key} = {value}",
        "unknown_setting": "Неизвестный параметр. Доступные: {keys}",
        "usage_set": "Использование: /set <параметр> <значение>",
        "rules_updated": "✅ Правила обновлены.",
        "welcome_updated": "✅ Приветствие обновлено.",
        "lang_updated": "✅ Язык переключён на русский.",
        "lang_usage": "Использование: /lang ru|en",
        "log_header": "📋 Последние действия:",
        "log_empty": "Записей пока нет.",
        "unban_usage": "Использование: /unban <user_id> (или ответом на сообщение).",
        "error": "Произошла ошибка при выполнении команды.",
        "reason_label": "Причина",
    },
    "en": {
        "start": (
            "Hi! I am a group moderation bot.\n"
            "Add me to a group and grant admin rights "
            "(ban, restrict, delete messages).\n"
            "Commands: /help"
        ),
        "help": (
            "Available commands:\n"
            "/rules — show the rules\n"
            "/warn — issue a warning (reply to a message)\n"
            "/mute [minutes] — mute a user\n"
            "/unmute — remove a mute\n"
            "/ban — ban a user\n"
            "/unban — unban (by id)\n"
            "/kick — remove from the chat\n"
            "/warns — a user's warning count\n"
            "/log — recent moderation actions\n"
            "/settings — current chat settings\n"
            "/set <key> <value> — change a setting\n"
            "/setrules <text> — set the rules\n"
            "/setwelcome <text> — set the welcome text\n"
            "/lang <ru|en> — bot language"
        ),
        "rules_not_set": "No rules set yet. An admin can set them via /setrules.",
        "captcha_prompt": (
            "{name}, to chat here solve this within {seconds}s:\n"
            "<b>{question}</b>"
        ),
        "captcha_pass": "Thanks, {name}! Verification passed.",
        "captcha_fail_wrong": "Wrong answer. Access denied.",
        "captcha_kick": "{name} failed verification and was removed.",
        "captcha_not_yours": "This challenge is not for you.",
        "not_admin": "This command is for administrators only.",
        "bot_not_admin": "I need admin rights (restrict and ban members).",
        "reply_required": "Reply to the offender's message with this command.",
        "cant_target_admin": "You cannot apply this action to an administrator.",
        "warn_issued": "⚠️ {name} gets a warning ({count}/{limit}). Reason: {reason}",
        "warn_muted": "🔇 {name} reached {count} warnings and is muted for {duration}.",
        "mute_issued": "🔇 {name} muted for {duration}. Reason: {reason}",
        "unmute_done": "🔊 {name} can write again.",
        "ban_issued": "⛔ {name} banned. Reason: {reason}",
        "unban_done": "✅ User {user_id} unbanned.",
        "kick_done": "👢 {name} removed from the chat.",
        "spam_deleted": "🧹 Message from {name} deleted ({reason}).",
        "flood_muted": "🔇 {name} muted for {duration} for flooding.",
        "warns_count": "{name} has active warnings: {count}/{limit}.",
        "no_reason": "not specified",
        "settings_header": "⚙️ Settings for «{title}»:",
        "setting_updated": "✅ {key} = {value}",
        "unknown_setting": "Unknown key. Available: {keys}",
        "usage_set": "Usage: /set <key> <value>",
        "rules_updated": "✅ Rules updated.",
        "welcome_updated": "✅ Welcome text updated.",
        "lang_updated": "✅ Language switched to English.",
        "lang_usage": "Usage: /lang ru|en",
        "log_header": "📋 Recent actions:",
        "log_empty": "No records yet.",
        "unban_usage": "Usage: /unban <user_id> (or reply to a message).",
        "error": "An error occurred while running the command.",
        "reason_label": "Reason",
    },
}


def normalize_lang(lang: str) -> str:
    lang = (lang or "").lower()
    return lang if lang in TEXTS else DEFAULT_LANG


def t(lang: str, key: str, **kwargs: Any) -> str:
    """Look up a localized string and format it with ``kwargs``."""
    lang = normalize_lang(lang)
    template = TEXTS[lang].get(key) or TEXTS[DEFAULT_LANG].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def default_rules(lang: str) -> str:
    return DEFAULT_RULES.get(normalize_lang(lang), DEFAULT_RULES[DEFAULT_LANG])


def default_welcome(lang: str) -> str:
    return DEFAULT_WELCOME.get(normalize_lang(lang), DEFAULT_WELCOME[DEFAULT_LANG])
