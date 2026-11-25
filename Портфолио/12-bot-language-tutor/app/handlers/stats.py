"""/stats: progress overview and typical-mistake breakdown.

Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .. import services
from ..config import Config
from ..i18n import error_type_label, t
from ..repository import Repository
from .common import get_user_ctx, is_onboarded, learn_lang_name

router = Router(name="stats")


@router.message(Command("stats"))
async def cmd_stats(
    message: Message, repo: Repository, cfg: Config, **_: Any
) -> None:
    user = await get_user_ctx(message, repo)
    ui_lang = user.get("ui_lang", "ru")
    if not is_onboarded(user):
        await message.answer(t("need_onboarding", ui_lang))
        return

    now = services.now_ts()
    today = services.today_str(cfg.tz)
    total = await repo.count_mistakes(message.from_user.id)
    due = await repo.count_due(message.from_user.id, now)
    remaining = await repo.remaining_quota(
        message.from_user.id, today, cfg.free_daily_limit
    )
    top_rows = await repo.top_error_types(message.from_user.id, limit=5)

    if top_rows:
        top = "\n".join(
            "• {} — {}".format(error_type_label(r["error_type"], ui_lang), r["n"])
            for r in top_rows
        )
    else:
        top = t("stats_no_mistakes", ui_lang)

    lang = learn_lang_name(user.get("learn_lang"), ui_lang)
    await message.answer(
        t(
            "stats",
            ui_lang,
            lang=lang,
            level=user.get("level") or "?",
            total=total,
            due=due,
            remaining=remaining,
            top=top,
        )
    )
