"""Participant-facing handlers: /start deep-links, join button, referral link."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from .. import i18n, logic
from ..config import Config
from ..db import Database
from ..keyboards import participate_kb
from ..services import is_subscribed

router = Router()
log = logging.getLogger(__name__)


def _lang(obj) -> str:
    user = getattr(obj, "from_user", None)
    code = getattr(user, "language_code", None) if user else None
    return i18n.normalize_lang(code or "ru")


async def _join(
    *, bot, db: Database, giveaway: dict, user, referrer_id, lang: str
) -> str:
    """Core join flow shared by /start deep-link and the inline button."""
    gid = int(giveaway["id"])

    if giveaway["status"] != "active":
        return i18n.t(lang, "giveaway_ended")

    # Channel subscription gate.
    channel = giveaway.get("required_channel")
    if channel and not await is_subscribed(bot, channel, user.id):
        return i18n.t(lang, "need_subscription", channel=channel)

    added = await db.add_participant(
        gid, user.id, user.username, getattr(user, "full_name", None)
    )

    # Credit referral only for a genuinely new participant with a valid referrer.
    if added and referrer_id and int(referrer_id) != int(user.id):
        # Referrer must themselves be a participant to earn the bonus.
        if await db.is_participant(gid, int(referrer_id)):
            await db.add_referral(gid, int(referrer_id), int(user.id))

    refs = await db.count_referrals(gid, user.id)
    tickets = logic.compute_tickets(1, refs, int(giveaway["points_per_ref"]))

    if not added:
        return i18n.t(lang, "already_joined")
    return i18n.t(lang, "join_ok", tickets=tickets)


@router.message(CommandStart(deep_link=True))
async def start_deeplink(message: Message, command: CommandObject, bot, db: Database, config: Config):
    lang = _lang(message)
    parsed = logic.parse_start_payload(command.args or "")
    gid = parsed.get("giveaway_id")
    referrer_id = parsed.get("referrer_id")

    giveaway = None
    if gid:
        giveaway = await db.get_giveaway(gid)
    if giveaway is None:
        giveaway = await db.latest_active_giveaway()
    if giveaway is None:
        await message.answer(i18n.t(lang, "start_no_giveaway"))
        return

    text = await _join(
        bot=bot, db=db, giveaway=giveaway, user=message.from_user,
        referrer_id=referrer_id, lang=lang,
    )
    await message.answer(text)


@router.message(CommandStart())
async def start_plain(message: Message, bot, db: Database, config: Config):
    lang = _lang(message)
    giveaway = await db.latest_active_giveaway()
    if giveaway is None:
        await message.answer(i18n.t(lang, "start_hello"))
        return
    await message.answer(
        i18n.t(lang, "start_hello"),
        reply_markup=participate_kb(int(giveaway["id"]), lang),
    )


@router.callback_query(F.data.startswith("join:"))
async def cb_join(cb: CallbackQuery, bot, db: Database, config: Config):
    lang = _lang(cb)
    gid = int(cb.data.split(":", 1)[1])
    giveaway = await db.get_giveaway(gid)
    if giveaway is None:
        await cb.answer(i18n.t(lang, "start_no_giveaway"), show_alert=True)
        return
    text = await _join(
        bot=bot, db=db, giveaway=giveaway, user=cb.from_user,
        referrer_id=None, lang=lang,
    )
    await cb.answer(text, show_alert=True)


@router.callback_query(F.data.startswith("reflink:"))
async def cb_reflink(cb: CallbackQuery, bot, db: Database, config: Config):
    lang = _lang(cb)
    gid = int(cb.data.split(":", 1)[1])
    giveaway = await db.get_giveaway(gid)
    if giveaway is None:
        await cb.answer(i18n.t(lang, "start_no_giveaway"), show_alert=True)
        return

    me = await bot.get_me()
    payload = logic.build_start_payload(gid, cb.from_user.id)
    link = f"https://t.me/{me.username}?start={payload}"

    refs = await db.count_referrals(gid, cb.from_user.id)
    tickets = logic.compute_tickets(1, refs, int(giveaway["points_per_ref"]))
    await cb.message.answer(
        i18n.t(lang, "your_ref_link", link=link, refs=refs, tickets=tickets)
    )
    await cb.answer()
