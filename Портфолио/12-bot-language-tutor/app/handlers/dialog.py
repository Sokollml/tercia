"""Free-conversation handler: correct, explain, store, reply.

This is the catch-all for plain text messages once the user is onboarded.  The
flow per message:

1. enforce the free-tier daily quota;
2. ask the LLM for a strict-JSON correction (graceful fallback on failure);
3. show the correction + explanation, or praise if clean;
4. persist any real mistake as a spaced-repetition item;
5. reply conversationally in the target language to keep the dialog going.

Compatible with Python 3.9.
"""
from __future__ import annotations

import logging
from typing import Any

from aiogram import F, Router
from aiogram.types import Message

from .. import services
from ..config import Config
from ..i18n import t
from ..llm import LLMClient, LLMError
from ..repository import Repository
from .common import get_user_ctx, is_onboarded, learn_lang_name

log = logging.getLogger("tutor.dialog")

router = Router(name="dialog")


@router.message(F.text & ~F.text.startswith("/"))
async def on_text(
    message: Message,
    repo: Repository,
    llm: LLMClient,
    cfg: Config,
    **_: Any,
) -> None:
    user = await get_user_ctx(message, repo)
    ui_lang = user.get("ui_lang", "ru")

    if not is_onboarded(user):
        await message.answer(t("need_onboarding", ui_lang))
        return

    today = services.today_str(cfg.tz)
    allowed = await repo.check_and_consume_quota(
        message.from_user.id, today, cfg.free_daily_limit
    )
    if not allowed:
        await message.answer(t("quota_reached", ui_lang, limit=cfg.free_daily_limit))
        return

    learn_lang = user.get("learn_lang") or "en"
    lang_name = learn_lang_name(learn_lang, ui_lang)
    level = user.get("level") or "A1"

    try:
        correction = await llm.analyse(
            user_text=message.text,
            learn_language=lang_name,
            level=level,
            ui_lang=ui_lang,
        )
    except LLMError as exc:
        log.warning("LLM failure for user %s: %s", message.from_user.id, exc)
        await message.answer(t("llm_unavailable", ui_lang))
        return
    except Exception as exc:  # pragma: no cover - unexpected, keep bot alive
        log.exception("Unexpected error analysing message: %s", exc)
        await message.answer(t("error_generic", ui_lang))
        return

    await _render_correction(message, repo, correction, user, ui_lang)


async def _render_correction(message, repo, correction, user, ui_lang) -> None:
    parts = []
    original = message.text.strip()
    corrected = (correction.corrected or "").strip()

    real_change = (
        correction.has_errors
        and corrected
        and corrected.casefold() != original.casefold()
    )

    if real_change:
        parts.append(t("corrected_header", ui_lang))
        parts.append("«{}»".format(corrected))
        if correction.explanation:
            parts.append(t("explanation_label", ui_lang, text=correction.explanation))
    else:
        parts.append(t("correct_praise", ui_lang))

    saved = False
    if real_change:
        try:
            await repo.add_mistake(
                user_id=message.from_user.id,
                original=original,
                corrected=corrected,
                explanation=correction.explanation,
                error_type=correction.error_type,
                now_ts=services.now_ts(),
            )
            saved = True
        except Exception as exc:  # pragma: no cover - persistence best effort
            logging.getLogger("tutor.dialog").warning("save mistake failed: %s", exc)

    if saved:
        parts.append(t("saved_mistake", ui_lang))

    if correction.reply:
        parts.append("")
        parts.append("💬 {}".format(correction.reply))

    await message.answer("\n".join(parts))
