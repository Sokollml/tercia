"""Spaced-repetition quiz flow.

`/quiz` pulls the mistakes whose ``next_review`` has arrived, then walks the user
through them one by one.  For each item the learner sees the prompt, reveals the
answer, then self-grades "got it / missed it".  The grade feeds :mod:`app.srs`
via the repository, which grows or resets the interval accordingly.

The per-session queue (list of mistake ids + cursor) lives in the FSM context.
Compatible with Python 3.9.
"""
from __future__ import annotations

from typing import Any, List

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import keyboards, services
from ..config import Config
from ..i18n import t
from ..repository import Repository
from ..srs import DAY_SECONDS
from ..states import Quiz
from .common import get_user_ctx, is_onboarded

router = Router(name="quiz")

QUIZ_BATCH = 10


@router.message(Command("quiz"))
async def cmd_quiz(
    message: Message, state: FSMContext, repo: Repository, cfg: Config, **_: Any
) -> None:
    user = await get_user_ctx(message, repo)
    ui_lang = user.get("ui_lang", "ru")
    if not is_onboarded(user):
        await message.answer(t("need_onboarding", ui_lang))
        return

    due = await repo.due_mistakes(message.from_user.id, services.now_ts(), QUIZ_BATCH)
    if not due:
        await message.answer(t("quiz_none_due", ui_lang))
        return

    queue: List[int] = [int(m["id"]) for m in due]
    await state.set_state(Quiz.answering)
    await state.update_data(quiz_queue=queue, quiz_pos=0, quiz_total=len(queue))
    await message.answer(t("quiz_intro", ui_lang, n=len(queue)))
    await _ask_current(message, state, repo, ui_lang)


async def _ask_current(target, state: FSMContext, repo: Repository, ui_lang: str) -> None:
    data = await state.get_data()
    queue: List[int] = data.get("quiz_queue", [])
    pos: int = data.get("quiz_pos", 0)
    total: int = data.get("quiz_total", len(queue))

    if pos >= len(queue):
        await state.clear()
        await target.answer(t("quiz_done", ui_lang, n=total))
        return

    mistake = await repo.get_mistake(queue[pos])
    if mistake is None:
        # Item vanished; skip forward.
        await state.update_data(quiz_pos=pos + 1)
        await _ask_current(target, state, repo, ui_lang)
        return

    prompt = mistake.get("original") or mistake.get("corrected") or ""
    await target.answer(
        t("quiz_question", ui_lang, i=pos + 1, n=total, prompt=prompt),
        reply_markup=keyboards.quiz_show_answer_keyboard(int(mistake["id"]), ui_lang),
    )


@router.callback_query(Quiz.answering, F.data.startswith(keyboards.CB_QUIZ_SHOW + ":"))
async def on_show_answer(cq: CallbackQuery, repo: Repository, **_: Any) -> None:
    _, values = keyboards.parse_callback(cq.data)
    mistake_id = int(values[0]) if values else 0
    user = await repo.get_user(cq.from_user.id)
    ui_lang = (user or {}).get("ui_lang", "ru")

    mistake = await repo.get_mistake(mistake_id)
    if mistake is None:
        await cq.answer()
        return

    answer = mistake.get("corrected") or ""
    explanation = mistake.get("explanation") or ""
    await cq.message.answer(
        t("quiz_answer", ui_lang, answer=answer, explanation=explanation),
        reply_markup=keyboards.quiz_grade_keyboard(mistake_id, ui_lang),
    )
    await cq.answer()


@router.callback_query(Quiz.answering, F.data.startswith(keyboards.CB_QUIZ_GRADE + ":"))
async def on_grade(
    cq: CallbackQuery, state: FSMContext, repo: Repository, **_: Any
) -> None:
    _, values = keyboards.parse_callback(cq.data)
    mistake_id = int(values[0]) if values else 0
    success = len(values) > 1 and values[1] == "1"

    user = await repo.get_user(cq.from_user.id)
    ui_lang = (user or {}).get("ui_lang", "ru")

    updated = await repo.apply_review(mistake_id, success, services.now_ts())
    if updated is not None and success:
        days = int(updated.get("interval_days") or 1)
        await cq.message.answer(t("quiz_progress_good", ui_lang, days=days))
    else:
        await cq.message.answer(t("quiz_progress_bad", ui_lang))

    data = await state.get_data()
    await state.update_data(quiz_pos=int(data.get("quiz_pos", 0)) + 1)
    await cq.answer()
    await _ask_current(cq.message, state, repo, ui_lang)
