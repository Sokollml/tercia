"""Префильтр сообщений БЕЗ ИИ.

Быстрый и дешёвый фильтр: пропускаем дальше (в БД на ИИ-классификацию)
только сообщения, которые похожи на заказ по ключевым словам и НЕ отсеяны
стоп-словами. Цель — резко сократить объём для дорогого ИИ-шага.

Логика намеренно консервативная: лучше пропустить лишнее (ИИ отсеет),
чем потерять реальный заказ.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

# Слова, характерные для поиска исполнителя.
KEYWORDS: List[str] = [
    "ищу", "ищем", "нужен", "нужна", "нужно", "требуется", "требуются",
    "ищется", "в поиске", "кто может", "кто возьмется", "кто возьмётся",
    "возьмется за", "возьмётся за", "заказ", "работа", "проект", "задача",
    "бюджет", "оплата", "оплачу", "плачу", "за деньги", "vacancy", "hiring",
    "looking for", "need a", "we need", "budget", "freelancer", "исполнител",
    "подрядчик", "фрилансер", "сделать", "разработать", "нарисовать",
    "написать", "смонтировать", "настроить",
]

# Слова, которые почти всегда означают НЕ заказ (резюме, реклама, оффтоп).
STOPWORDS: List[str] = [
    "ищу работу", "ищу заказы", "ищу проекты", "резюме", "моё портфолио",
    "мое портфолио", "готов взяться", "возьму заказ", "делаю сайты",
    "предлагаю услуги", "мои услуги", "обучение", "курс", "вебинар",
    "скидка", "розыгрыш", "продам", "продаю", "куплю аккаунт",
    "looking for work", "available for hire", "my portfolio", "for sale",
    "промокод", "реферальн", "заработок в интернете", "инвестиции",
]

# Минимальная длина осмысленного сообщения (символов).
MIN_LENGTH = 15


def _normalize(text: str) -> str:
    """Нижний регистр + схлопывание пробелов. Для сравнения по подстроке."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_any(text_norm: str, needles: Iterable[str]) -> Optional[str]:
    """Вернуть первое найденное вхождение из needles или None."""
    for n in needles:
        if n in text_norm:
            return n
    return None


def passes_prefilter(
    text: Optional[str],
    keywords: Optional[Iterable[str]] = None,
    stopwords: Optional[Iterable[str]] = None,
) -> bool:
    """True -> сообщение стоит отправить на ИИ-классификацию.

    Правила:
    - пустое/слишком короткое -> False
    - есть стоп-слово -> False (даже если есть ключевое)
    - есть хотя бы одно ключевое слово -> True
    - иначе -> False
    """
    if not text:
        return False

    norm = _normalize(text)
    if len(norm) < MIN_LENGTH:
        return False

    kw = list(keywords) if keywords is not None else KEYWORDS
    sw = list(stopwords) if stopwords is not None else STOPWORDS

    if contains_any(norm, sw) is not None:
        return False

    return contains_any(norm, kw) is not None
