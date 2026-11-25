"""Master-facing handlers: day schedule, cancel booking, close/add slot.

Every handler is guarded by the ``is_master`` flag injected by the middleware,
so client accounts cannot reach master actions even if they guess callbacks.
"""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import Config
from ..keyboards import master_menu, schedule_kb
from ..repository import Repository
from ..services import day_bounds, format_day, format_when, now_ts, parse_slot_input
from ..states import MasterFlow
from ..texts import t

log = logging.getLogger("booking.master")
router = Router(name="master")


@router.message(Command("master"))
async def cmd_master(message: Message, lang: str, is_master: bool) -> None:
    if not is_master:
        await message.answer(t("master_only", lang))
        return
    await message.answer(t("master_menu", lang), reply_markup=master_menu(lang))


@router.callback_query(F.data == "master")
async def cb_master(call: CallbackQuery, lang: str, is_master: bool) -> None:
    if not is_master:
        await call.answer(t("master_only", lang), show_alert=True)
        return
    await call.message.edit_text(t("master_menu", lang), reply_markup=master_menu(lang))
    await call.answer()


@router.callback_query(F.data == "m_schedule")
async def cb_schedule(
    call: CallbackQuery, repo: Repository, config: Config, lang: str, is_master: bool
) -> None:
    if not is_master:
        await call.answer(t("master_only", lang), show_alert=True)
        return
    master_id = call.from_user.id
    start, end = day_bounds(now_ts(), config.tz)
    bookings = await repo.bookings_for_day(master_id, start, end)
    slots = await repo.list_slots_between(master_id, start, end)

    lines = [t("schedule_header", lang, day=format_day(start, config.tz))]
    for b in bookings:
        lines.append(
            t(
                "schedule_line_booked",
                lang,
                when=format_when(b["start_ts"], config.tz),
                service=b["service_title"],
                client=b["client_name"] or b["client_id"],
                id=b["id"],
            )
        )

    # Determine which slots are free (no confirmed booking) vs closed.
    free_slots = []
    booked_starts = {b["start_ts"] for b in bookings}
    for s in slots:
        if s["is_closed"]:
            lines.append(
                t("schedule_line_closed", lang, when=format_when(s["start_ts"], config.tz))
            )
        elif s["start_ts"] in booked_starts:
            continue  # already listed as booked above
        else:
            free_slots.append(s)
            lines.append(
                t("schedule_line_free", lang, when=format_when(s["start_ts"], config.tz))
            )

    if not bookings and not slots:
        lines.append(t("schedule_empty", lang))

    await call.message.edit_text(
        "\n".join(lines), reply_markup=schedule_kb(bookings, free_slots, lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("m_cxl:"))
async def cb_master_cancel(
    call: CallbackQuery, repo: Repository, config: Config, lang: str, is_master: bool
) -> None:
    if not is_master:
        await call.answer(t("master_only", lang), show_alert=True)
        return
    booking_id = int(call.data.split(":", 1)[1])
    full = await repo.get_booking_full(booking_id)
    if full is None:
        await call.answer(t("error_generic", lang), show_alert=True)
        return
    await repo.cancel_booking(booking_id)
    # Notify the client in their own language.
    client_id = full["client_id"]
    try:
        await call.bot.send_message(
            client_id,
            t(
                "client_notified_cancel",
                lang,
                when=format_when(full["start_ts"], config.tz),
                service=full["service_title"],
            ),
        )
    except Exception:  # pragma: no cover - client may have blocked the bot
        log.warning("could not notify client %s about cancellation", client_id)
    await call.message.edit_text(
        t("master_cancelled", lang, id=booking_id), reply_markup=master_menu(lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("m_close:"))
async def cb_close_slot(
    call: CallbackQuery, repo: Repository, lang: str, is_master: bool
) -> None:
    if not is_master:
        await call.answer(t("master_only", lang), show_alert=True)
        return
    slot_id = int(call.data.split(":", 1)[1])
    await repo.close_slot(slot_id)
    await call.message.edit_text(t("slot_closed_ok", lang), reply_markup=master_menu(lang))
    await call.answer()


@router.callback_query(F.data == "m_addslot")
async def cb_add_slot_prompt(
    call: CallbackQuery, state: FSMContext, lang: str, is_master: bool
) -> None:
    if not is_master:
        await call.answer(t("master_only", lang), show_alert=True)
        return
    await state.set_state(MasterFlow.adding_slot)
    await call.message.edit_text(t("add_slot_prompt", lang))
    await call.answer()


@router.message(MasterFlow.adding_slot)
async def on_add_slot(
    message: Message,
    state: FSMContext,
    repo: Repository,
    config: Config,
    lang: str,
    is_master: bool,
) -> None:
    if not is_master:
        await state.clear()
        return
    start_ts = parse_slot_input(message.text or "", config.tz)
    if start_ts is None:
        await message.answer(t("add_slot_bad", lang))
        return
    if start_ts <= now_ts():
        await message.answer(t("add_slot_past", lang))
        return
    await repo.add_slot(message.from_user.id, start_ts, start_ts + 3600)
    await state.clear()
    await message.answer(
        t("add_slot_ok", lang, when=format_when(start_ts, config.tz)),
        reply_markup=master_menu(lang),
    )
