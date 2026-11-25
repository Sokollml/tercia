"""Tiny bilingual (RU/EN) interface catalogue.

No framework, no gettext — just a nested dict of message templates keyed by UI
language.  :func:`t` looks a key up, formats it with ``**kwargs`` and always
falls back gracefully (English → key) so a missing translation never crashes a
handler.  Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Dict

DEFAULT_UI_LANG = "ru"

# key -> {ui_lang -> template}
_TEXTS: Dict[str, Dict[str, str]] = {
    "start": {
        "ru": (
            "Привет! Я — ИИ-репетитор языка. \n\n"
            "Пиши мне на изучаемом языке, а я мягко исправлю ошибки, объясню их "
            "и буду возвращать их тебе мини-квизами по интервальным повторениям.\n\n"
            "Для начала выбери язык интерфейса:"
        ),
        "en": (
            "Hi! I'm your AI language tutor.\n\n"
            "Write to me in the language you're learning — I'll gently correct "
            "mistakes, explain them and bring them back as spaced-repetition "
            "mini-quizzes.\n\n"
            "First, choose your interface language:"
        ),
    },
    "choose_learn_lang": {
        "ru": "Какой язык учим?",
        "en": "Which language are you learning?",
    },
    "choose_level": {
        "ru": "Отлично! Твой уровень ({lang})?",
        "en": "Great! What's your level ({lang})?",
    },
    "onboarding_done": {
        "ru": (
            "Готово! Учим {lang}, уровень {level}.\n\n"
            "Просто напиши мне сообщение на {lang} — и поехали. "
            "Команды: /quiz — повторение ошибок, /stats — статистика, "
            "/help — помощь."
        ),
        "en": (
            "All set! Learning {lang}, level {level}.\n\n"
            "Just send me a message in {lang} and we're off. "
            "Commands: /quiz — review mistakes, /stats — statistics, "
            "/help — help."
        ),
    },
    "need_onboarding": {
        "ru": "Сначала настроим бота — набери /start.",
        "en": "Let's set things up first — send /start.",
    },
    "help": {
        "ru": (
            "Я репетитор языка. Пиши на изучаемом языке — исправлю и объясню.\n\n"
            "/start — заново выбрать язык и уровень\n"
            "/quiz — повторить накопленные ошибки\n"
            "/stats — прогресс и типичные ошибки\n"
            "/cancel — прервать текущий диалог или квиз\n"
            "/help — эта справка"
        ),
        "en": (
            "I'm your language tutor. Write in your target language — I'll "
            "correct and explain.\n\n"
            "/start — pick language and level again\n"
            "/quiz — review collected mistakes\n"
            "/stats — progress and typical mistakes\n"
            "/cancel — stop the current dialog or quiz\n"
            "/help — this help"
        ),
    },
    "cancelled": {
        "ru": "Ок, остановились. Пиши, когда захочешь продолжить.",
        "en": "Okay, stopped. Message me whenever you want to continue.",
    },
    "nothing_to_cancel": {
        "ru": "Сейчас нечего отменять.",
        "en": "Nothing to cancel right now.",
    },
    "corrected_header": {
        "ru": "✏️ Исправление",
        "en": "✏️ Correction",
    },
    "correct_praise": {
        "ru": "👍 Всё верно!",
        "en": "👍 All correct!",
    },
    "explanation_label": {
        "ru": "💡 {text}",
        "en": "💡 {text}",
    },
    "saved_mistake": {
        "ru": "📌 Запомнил ошибку — вернусь к ней позже.",
        "en": "📌 Saved this one — I'll bring it back later.",
    },
    "llm_unavailable": {
        "ru": "⚠️ Не получилось связаться с ИИ. Попробуй ещё раз чуть позже.",
        "en": "⚠️ Couldn't reach the AI. Please try again a bit later.",
    },
    "quota_reached": {
        "ru": (
            "🚦 На сегодня бесплатный лимит исправлений ({limit}) исчерпан. "
            "Возвращайся завтра или потренируй ошибки: /quiz."
        ),
        "en": (
            "🚦 You've hit today's free correction limit ({limit}). "
            "Come back tomorrow or practise mistakes: /quiz."
        ),
    },
    "rate_limited": {
        "ru": "⏳ Слишком быстро — подожди секунду.",
        "en": "⏳ Too fast — hold on a second.",
    },
    "quiz_none_due": {
        "ru": "🎉 Сейчас нечего повторять. Пиши мне — соберём новые темы!",
        "en": "🎉 Nothing to review right now. Chat with me to collect more!",
    },
    "quiz_intro": {
        "ru": "🧠 Мини-квиз: {n} ошибок на повторение. Переведи/исправь:",
        "en": "🧠 Mini-quiz: {n} mistakes to review. Translate/fix:",
    },
    "quiz_question": {
        "ru": "Вопрос {i}/{n}\n\nКак правильно?\n\n«{prompt}»",
        "en": "Question {i}/{n}\n\nWhat's the correct form?\n\n“{prompt}”",
    },
    "quiz_show_answer": {
        "ru": "Показать ответ",
        "en": "Show answer",
    },
    "quiz_answer": {
        "ru": "✅ Правильный ответ:\n«{answer}»\n\n💡 {explanation}",
        "en": "✅ Correct answer:\n“{answer}”\n\n💡 {explanation}",
    },
    "quiz_self_grade": {
        "ru": "Как справился?",
        "en": "How did you do?",
    },
    "quiz_grade_good": {
        "ru": "✅ Помнил",
        "en": "✅ Got it",
    },
    "quiz_grade_bad": {
        "ru": "❌ Забыл",
        "en": "❌ Missed it",
    },
    "quiz_progress_good": {
        "ru": "Отлично! Следующее повторение — через {days} дн.",
        "en": "Nice! Next review in {days} day(s).",
    },
    "quiz_progress_bad": {
        "ru": "Ничего, повторим скоро ещё раз.",
        "en": "No worries, we'll revisit it soon.",
    },
    "quiz_done": {
        "ru": "Готово! Повторили {n} шт. Возвращайся за новой порцией: /quiz.",
        "en": "Done! Reviewed {n}. Come back for more: /quiz.",
    },
    "stats": {
        "ru": (
            "📊 Твоя статистика\n\n"
            "Язык: {lang} ({level})\n"
            "Всего ошибок собрано: {total}\n"
            "На повторение сейчас: {due}\n"
            "Осталось исправлений сегодня: {remaining}\n\n"
            "Типичные ошибки:\n{top}"
        ),
        "en": (
            "📊 Your statistics\n\n"
            "Language: {lang} ({level})\n"
            "Mistakes collected: {total}\n"
            "Due for review now: {due}\n"
            "Corrections left today: {remaining}\n\n"
            "Typical mistakes:\n{top}"
        ),
    },
    "stats_no_mistakes": {
        "ru": "— пока пусто, пиши мне —",
        "en": "— empty so far, chat with me —",
    },
    "reminder": {
        "ru": "🔔 У тебя {n} ошибок ждут повторения. Запусти /quiz!",
        "en": "🔔 You have {n} mistakes waiting. Run /quiz!",
    },
    "error_generic": {
        "ru": "😔 Что-то пошло не так. Попробуй ещё раз.",
        "en": "😔 Something went wrong. Please try again.",
    },
}

# Human-readable error-type labels for the /stats breakdown.
ERROR_TYPE_LABELS: Dict[str, Dict[str, str]] = {
    "grammar": {"ru": "грамматика", "en": "grammar"},
    "vocabulary": {"ru": "лексика", "en": "vocabulary"},
    "spelling": {"ru": "орфография", "en": "spelling"},
    "word_order": {"ru": "порядок слов", "en": "word order"},
    "punctuation": {"ru": "пунктуация", "en": "punctuation"},
    "article": {"ru": "артикли", "en": "articles"},
    "preposition": {"ru": "предлоги", "en": "prepositions"},
    "tense": {"ru": "времена", "en": "tenses"},
    "agreement": {"ru": "согласование", "en": "agreement"},
    "style": {"ru": "стиль", "en": "style"},
    "other": {"ru": "прочее", "en": "other"},
}


def normalise_ui_lang(ui_lang: str) -> str:
    """Return a supported UI language, defaulting to Russian."""
    lang = (ui_lang or "").lower()
    return lang if lang in {"ru", "en"} else DEFAULT_UI_LANG


def t(key: str, ui_lang: str = DEFAULT_UI_LANG, **kwargs: object) -> str:
    """Look up and format a message for ``ui_lang``.

    Falls back to English and then to the raw key so a missing entry degrades
    to something printable rather than raising.
    """
    lang = normalise_ui_lang(ui_lang)
    entry = _TEXTS.get(key)
    if entry is None:
        return key
    template = entry.get(lang) or entry.get("en") or next(iter(entry.values()), key)
    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, IndexError):  # pragma: no cover - defensive
        return template


def error_type_label(error_type: str, ui_lang: str = DEFAULT_UI_LANG) -> str:
    lang = normalise_ui_lang(ui_lang)
    entry = ERROR_TYPE_LABELS.get(error_type, ERROR_TYPE_LABELS["other"])
    return entry.get(lang, error_type)
