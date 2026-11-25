"""Client-facing handlers: booking flow, my bookings, language."""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import Config
from ..keyboards import (
    confirm_kb,
    lang_kb,
    main_menu,
    my_bookings_kb,
    services_kb,
    slots_kb,
)
from ..repository import Repository, SlotUnavailableError
from ..services import format_when, now_ts
from ..states import BookingFlow
from ..texts import t

log = logging.getLogger("booking.client")
router = Router(name="client")


async def _show_main(message: Message, lang: str, is_master: bool, name: str) -> None:
    await message.answer(
        t("welcome", lang, name=name), reply_markup=main_menu(lang, is_master)
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str, is_master: bool) -> None:
    await state.clear()
    await _show_main(message, lang, is_master, message.from_user.first_name or "")


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str, is_master: bool) -> None:
    await _show_main(message, lang, is_master, message.from_user.first_name or "")


@router.callback_query(F.data == "home")
async def cb_home(call: CallbackQuery, state: FSMContext, lang: str, is_master: bool) -> None:
    await state.clear()
    await call.message.edit_text(
        t("welcome", lang, name=call.from_user.first_name or ""),
        reply_markup=main_menu(lang, is_master),
    )
    await call.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(call: CallbackQuery, state: FSMContext, lang: str, is_master: bool) -> None:
    await state.clear()
    await call.message.edit_text(t("cancelled", lang), reply_markup=main_menu(lang, is_master))
    await call.answer()


# ---- Language -----------------------------------------------------------
@router.callback_query(F.data == "lang")
async def cb_lang(call: CallbackQuery, lang: str) -> None:
    await call.message.edit_text(t("lang_choose", lang), reply_markup=lang_kb())
    await call.answer()


@router.callback_query(F.data.startswith("setlang:"))
async def cb_setlang(call: CallbackQuery, lang_store, is_master: bool) -> None:
    new_lang = call.data.split(":", 1)[1]
    lang_store[call.from_user.id] = new_lang
    await call.message.edit_text(
        t("lang_set", new_lang), reply_markup=main_menu(new_lang, is_master)
    )
    await call.answer()


# ---- Booking flow -------------------------------------------------------
@router.callback_query(F.data == "book")
async def cb_book(
    call: CallbackQuery, state: FSMContext, repo: Repository, config: Config, lang: str
) -> None:
    master_id = config.master_ids[0] if config.master_ids else await repo.any_master_id()
    if master_id is None:
        await call.answer(t("no_services", lang), show_alert=True)
        return
    services = await repo.list_services(master_id)
    if not services:
        await call.message.edit_text(t("no_services", lang))
        await call.answer()
        return
    await state.set_state(BookingFlow.choosing_service)
    await state.update_data(master_id=master_id)
    await call.message.edit_text(
        t("choose_service", lang), reply_markup=services_kb(services, lang)
    )
    await call.answer()


@router.callback_query(BookingFlow.choosing_service, F.data.startswith("svc:"))
async def cb_pick_service(
    call: CallbackQuery, state: FSMContext, repo: Repository, config: Config, lang: str
) -> None:
    service_id = int(call.data.split(":", 1)[1])
    service = await repo.get_service(service_id)
    if service is None:
        await call.answer(t("error_generic", lang), show_alert=True)
        return
    data = await state.get_data()
    master_id = data.get("master_id", service["master_id"])
    slots = await repo.list_free_slots(master_id, now_ts())
    if not slots:
        await call.message.edit_text(t("no_slots", lang))
        await state.clear()
        await call.answer()
        return
    await state.set_state(BookingFlow.choosing_slot)
    await state.update_data(service_id=service_id)
    await call.message.edit_text(
        t("choose_slot", lang, service=service["title"]),
        reply_markup=slots_kb(slots, config.tz, lang),
    )
    await call.answer()


@router.callback_query(BookingFlow.choosing_slot, F.data.startswith("slot:"))
async def cb_pick_slot(
    call: CallbackQuery, state: FSMContext, repo: Repository, config: Config, lang: str
) -> None:
    slot_id = int(call.data.split(":", 1)[1])
    slot = await repo.get_slot(slot_id)
    data = await state.get_data()
    service = await repo.get_service(data.get("service_id"))
    if slot is None or service is None or not await repo.is_slot_free(slot_id):
        await call.answer(t("slot_taken", lang), show_alert=True)
        return
    await state.set_state(BookingFlow.confirming)
    await state.update_data(slot_id=slot_id)
    await call.message.edit_text(
        t(
            "confirm",
            lang,
            service=service["title"],
            when=format_when(slot["start_ts"], config.tz),
            price=service["price"],
        ),
        reply_markup=confirm_kb(slot_id, service["id"], lang),
    )
    await call.answer()


@router.callback_query(BookingFlow.confirming, F.data.startswith("confirm:"))
async def cb_confirm(
    call: CallbackQuery,
    state: FSMContext,
    repo: Repository,
    config: Config,
    lang: str,
    is_master: bool,
) -> None:
    _, slot_id_s, service_id_s = call.data.split(":")
    slot_id, service_id = int(slot_id_s), int(service_id_s)
    slot = await repo.get_slot(slot_id)
    service = await repo.get_service(service_id)
    if slot is None or service is None:
        await call.answer(t("error_generic", lang), show_alert=True)
        await state.clear()
        return
    try:
        await repo.create_booking(
            slot_id=slot_id,
            service_id=service_id,
            client_id=call.from_user.id,
            client_name=call.from_user.full_name,
            created_at=now_ts(),
        )
    except SlotUnavailableError:
        await call.answer(t("slot_taken", lang), show_alert=True)
        await state.clear()
        await call.message.edit_text(t("slot_taken", lang), reply_markup=main_menu(lang, is_master))
        return
    await state.clear()
    await call.message.edit_text(
        t(
            "booked_ok",
            lang,
            when=format_when(slot["start_ts"], config.tz),
            service=service["title"],
        ),
        reply_markup=main_menu(lang, is_master),
    )
    await call.answer()
    log.info("booking created: user=%s slot=%s", call.from_user.id, slot_id)


# ---- My bookings --------------------------------------------------------
@router.callback_query(F.data == "my")
async def cb_my(call: CallbackQuery, repo: Repository, config: Config, lang: str) -> None:
    bookings = await repo.list_client_bookings(call.from_user.id, now_ts())
    if not bookings:
        await call.message.edit_text(t("my_empty", lang))
        await call.answer()
        return
    lines = [
        t(
            "my_item",
            lang,
            when=format_when(b["start_ts"], config.tz),
            service=b["service_title"],
            id=b["id"],
        )
        for b in bookings
    ]
    await call.message.edit_text(
        "\n".join(lines), reply_markup=my_bookings_kb(bookings, lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("cxl:"))
async def cb_cancel_booking(call: CallbackQuery, repo: Repository, lang: str, is_master: bool) -> None:
    booking_id = int(call.data.split(":", 1)[1])
    booking = await repo.get_booking(booking_id)
    if booking is None or booking["client_id"] != call.from_user.id:
        await call.answer(t("error_generic", lang), show_alert=True)
        return
    await repo.cancel_booking(booking_id)
    await call.message.edit_text(
        t("booking_cancelled", lang, id=booking_id), reply_markup=main_menu(lang, is_master)
    )
    await call.answer()
