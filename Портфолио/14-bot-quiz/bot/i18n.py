"""Tiny RU/EN internationalisation helper.

No external gettext machinery: the bot only needs a small set of strings, so a
plain nested dict keeps things dependency-free and easy to read.
"""
from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "ru"
SUPPORTED = ("ru", "en")

_STRINGS: Dict[str, Dict[str, str]] = {
    "start": {
        "ru": (
            "Привет! Я бот-викторина для сообществ.\n\n"
            "Добавьте меня в группу и назначьте администратором, чтобы я мог "
            "публиковать вопросы. Команда /help покажет список команд."
        ),
        "en": (
            "Hi! I am a community quiz bot.\n\n"
            "Add me to a group and make me an admin so I can post questions. "
            "Use /help to see the list of commands."
        ),
    },
    "help_user": {
        "ru": (
            "<b>Команды участника</b>\n"
            "/leaderboard — таблица лидеров сезона\n"
            "/myscore — ваши очки\n"
            "/lang ru|en — язык бота\n"
            "/help — эта справка"
        ),
        "en": (
            "<b>Player commands</b>\n"
            "/leaderboard — season leaderboard\n"
            "/myscore — your score\n"
            "/lang ru|en — bot language\n"
            "/help — this help"
        ),
    },
    "help_admin": {
        "ru": (
            "\n\n<b>Команды администратора</b>\n"
            "/quiz [категория] — задать один вопрос\n"
            "/marathon [категория] — серия вопросов подряд\n"
            "/blitz [категория] — быстрый блиц\n"
            "/addquestion — добавить вопрос (мастер)\n"
            "/daily on|off — авто-вопрос дня по расписанию\n"
            "/newseason Название — начать новый сезон\n"
            "/endseason — подвести итоги и закрыть сезон\n"
            "/results — текущие итоги сезона\n"
            "/categories — список категорий"
        ),
        "en": (
            "\n\n<b>Admin commands</b>\n"
            "/quiz [category] — ask a single question\n"
            "/marathon [category] — a series of questions\n"
            "/blitz [category] — fast blitz round\n"
            "/addquestion — add a question (wizard)\n"
            "/daily on|off — scheduled daily question\n"
            "/newseason Title — start a new season\n"
            "/endseason — wrap up and close the season\n"
            "/results — current season standings\n"
            "/categories — list categories"
        ),
    },
    "not_admin": {
        "ru": "Эта команда доступна только администраторам бота.",
        "en": "This command is available to bot admins only.",
    },
    "group_only": {
        "ru": "Викторину можно запускать только в группе.",
        "en": "A quiz can only be started inside a group.",
    },
    "no_questions": {
        "ru": "В банке нет вопросов для этой категории/языка. Пополните банк через /addquestion.",
        "en": "No questions in the bank for this category/language. Add some via /addquestion.",
    },
    "no_active_season": {
        "ru": "Нет активного сезона. Создайте его командой /newseason Название.",
        "en": "No active season. Start one with /newseason Title.",
    },
    "quiz_intro": {
        "ru": "Вопрос дня! Категория: {category}",
        "en": "Question of the day! Category: {category}",
    },
    "marathon_intro": {
        "ru": "Марафон из {n} вопросов начинается! Отвечайте быстрее для бонуса.",
        "en": "A marathon of {n} questions begins! Answer faster for a bonus.",
    },
    "blitz_intro": {
        "ru": "Блиц! {n} быстрых вопросов подряд.",
        "en": "Blitz! {n} rapid-fire questions.",
    },
    "leaderboard_title": {
        "ru": "🏆 Таблица лидеров сезона «{season}»",
        "en": "🏆 Leaderboard — season \"{season}\"",
    },
    "leaderboard_empty": {
        "ru": "Пока никто не набрал очков. Будьте первым!",
        "en": "No points yet. Be the first!",
    },
    "myscore": {
        "ru": "Ваш счёт в сезоне «{season}»: {points} очк. (верных ответов: {correct}/{total}).",
        "en": "Your score in season \"{season}\": {points} pts (correct: {correct}/{total}).",
    },
    "myscore_none": {
        "ru": "Вы ещё не отвечали в этом сезоне.",
        "en": "You have not answered anything this season yet.",
    },
    "season_started": {
        "ru": "Новый сезон «{season}» начат! Прошлые очки обнулены.",
        "en": "New season \"{season}\" started! Previous scores were reset.",
    },
    "season_ended": {
        "ru": "🎉 Сезон «{season}» завершён!",
        "en": "🎉 Season \"{season}\" has ended!",
    },
    "winners": {
        "ru": "Поздравляем победителей:",
        "en": "Congratulations to the winners:",
    },
    "lang_set": {
        "ru": "Язык бота переключён на русский.",
        "en": "Bot language switched to English.",
    },
    "lang_usage": {
        "ru": "Использование: /lang ru или /lang en",
        "en": "Usage: /lang ru or /lang en",
    },
    "categories_title": {
        "ru": "Доступные категории:",
        "en": "Available categories:",
    },
    "rate_limited": {
        "ru": "Слишком часто. Подождите секунду и повторите.",
        "en": "Too fast. Wait a second and try again.",
    },
    "error_generic": {
        "ru": "Упс, что-то пошло не так. Попробуйте ещё раз позже.",
        "en": "Oops, something went wrong. Please try again later.",
    },
    # /addquestion wizard
    "aq_category": {
        "ru": "Введите категорию вопроса (например: История):",
        "en": "Enter the question category (e.g. History):",
    },
    "aq_lang": {
        "ru": "Язык вопроса? Отправьте ru или en:",
        "en": "Question language? Send ru or en:",
    },
    "aq_text": {
        "ru": "Введите текст вопроса:",
        "en": "Enter the question text:",
    },
    "aq_options": {
        "ru": (
            "Введите варианты ответа, каждый с новой строки (от 2 до 10). "
            "Правильный вариант отметьте звёздочкой * в начале строки."
        ),
        "en": (
            "Enter answer options, one per line (2 to 10). "
            "Mark the correct one with a leading asterisk *."
        ),
    },
    "aq_saved": {
        "ru": "Вопрос сохранён (id={id}, категория: {category}).",
        "en": "Question saved (id={id}, category: {category}).",
    },
    "aq_bad_options": {
        "ru": "Нужно 2–10 вариантов и ровно один правильный (со *). Попробуйте снова.",
        "en": "Need 2–10 options and exactly one correct (marked with *). Try again.",
    },
    "aq_cancelled": {
        "ru": "Добавление вопроса отменено.",
        "en": "Adding a question was cancelled.",
    },
    "newseason_usage": {
        "ru": "Использование: /newseason Название сезона",
        "en": "Usage: /newseason Season title",
    },
    "daily_usage": {
        "ru": "Использование: /daily on или /daily off",
        "en": "Usage: /daily on or /daily off",
    },
    "daily_on": {
        "ru": "Вопрос дня включён. Я буду публиковать его по расписанию.",
        "en": "Daily question enabled. I will post it on schedule.",
    },
    "daily_off": {
        "ru": "Вопрос дня выключен для этого чата.",
        "en": "Daily question disabled for this chat.",
    },
    "results_title": {
        "ru": "📊 Текущие итоги сезона «{season}»",
        "en": "📊 Current standings — season \"{season}\"",
    },
}


def normalize_lang(lang: str) -> str:
    lang = (lang or "").lower()
    return lang if lang in SUPPORTED else DEFAULT_LANG


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Translate ``key`` into ``lang`` with optional ``str.format`` kwargs."""
    lang = normalize_lang(lang)
    entry = _STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
