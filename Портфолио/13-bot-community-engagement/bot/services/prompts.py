"""Question-of-the-day / poll pool and picker."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import DailyPrompt

# Built-in pool used to seed an empty DB.
SEED_PROMPTS = [
    {
        "kind": "question",
        "text_ru": "Какой навык вы хотели бы освоить в этом году?",
        "text_en": "What skill would you love to learn this year?",
    },
    {
        "kind": "question",
        "text_ru": "Фильм или сериал, который недавно зацепил — почему?",
        "text_en": "A movie or show that recently hooked you — why?",
    },
    {
        "kind": "question",
        "text_ru": "Расскажите о маленькой победе за эту неделю 🎉",
        "text_en": "Share a small win from your week 🎉",
    },
    {
        "kind": "poll",
        "text_ru": "Как вам больше нравится работать?",
        "text_en": "How do you prefer to work?",
        "options_ru": "Утром|Днём|Вечером|Ночью",
        "options_en": "Morning|Afternoon|Evening|Night",
    },
    {
        "kind": "poll",
        "text_ru": "Кофе или чай?",
        "text_en": "Coffee or tea?",
        "options_ru": "Кофе|Чай|Ни то, ни другое",
        "options_en": "Coffee|Tea|Neither",
    },
]


@dataclass
class PromptView:
    kind: str
    text: str
    options: Optional[List[str]]


async def seed_prompts(session: AsyncSession) -> int:
    """Insert built-in prompts if the table is empty. Returns count added."""
    existing = (await session.execute(select(func.count()).select_from(DailyPrompt))).scalar_one()
    if existing:
        return 0
    for p in SEED_PROMPTS:
        session.add(
            DailyPrompt(
                chat_id=None,
                kind=p["kind"],
                text_ru=p["text_ru"],
                text_en=p["text_en"],
                options_ru=p.get("options_ru"),
                options_en=p.get("options_en"),
            )
        )
    await session.flush()
    return len(SEED_PROMPTS)


async def pick_prompt(session: AsyncSession, chat_id: int, lang: str = "ru") -> Optional[PromptView]:
    """Random prompt for a chat (chat-specific first, else global pool)."""
    stmt = select(DailyPrompt).where(
        (DailyPrompt.chat_id == chat_id) | (DailyPrompt.chat_id.is_(None))
    )
    rows = (await session.execute(stmt)).scalars().all()
    if not rows:
        return None
    p = random.choice(rows)
    text = p.text_ru if lang == "ru" else p.text_en
    opts_raw = p.options_ru if lang == "ru" else p.options_en
    options = [o for o in opts_raw.split("|") if o] if opts_raw else None
    return PromptView(kind=p.kind, text=text, options=options)
