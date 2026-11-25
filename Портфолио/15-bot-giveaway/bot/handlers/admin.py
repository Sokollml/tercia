"""Admin handlers: create giveaway, stats, participant list, force finish."""

from __future__ import annotations

import logging
from datetime import timedelta
from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .. import i18n, logic
from ..config import Config
from ..db import Database, _now_utc
from ..keyboards import participate_kb
from ..services import run_draw

router = Router()
log = logging.getLogger(__name__)


def _lang(message: Message) -> str:
    code = getattr(message.from_user, "language_code", None)
    return i18n.normalize_lang(code or "ru")


def _require_admin(message: Message, config: Config) -> bool:
    return config.is_admin(message.from_user.id)


@router.message(Command("new_giveaway"))
async def cmd_new_giveaway(message: Message, bot, db: Database, config: Config):
    lang = _lang(message)
    if not _require_admin(message, config):
        await message.answer(i18n.t(lang, "admin_only"))
        return

    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        await message.answer(i18n.t(lang, "new_giveaway_prompt"))
        return

    # Format: <prize> | <winners> | <hours> | <@channel|->
    parts = [p.strip() for p in args[1].split("|")]
    if len(parts) < 3:
        await message.answer(i18n.t(lang, "new_giveaway_bad"))
        return
    prize = parts[0]
    try:
        winners_count = max(1, int(parts[1]))
        hours = float(parts[2])
    except ValueError:
        await message.answer(i18n.t(lang, "new_giveaway_bad"))
        return
    channel = None
    if len(parts) >= 4 and parts[3] and parts[3] != "-":
        channel = parts[3]

    seed = logic.generate_seed()
    ends_at = _now_utc() + timedelta(hours=hours)

    gid = await db.create_giveaway(
        chat_id=message.chat.id,
        creator_id=message.from_user.id,
        prize=prize,
        description="",
        winners_count=winners_count,
        points_per_ref=1,
        required_channel=channel,
        seed=seed,
        ends_at=ends_at,
    )

    announce = i18n.t(
        lang, "announce",
        prize=escape(prize), description="",
        winners=winners_count, ends=ends_at.strftime("%Y-%m-%d %H:%M UTC"),
    )
    sent = await message.answer(announce, reply_markup=participate_kb(gid, lang))
    await db.set_announce_msg(gid, sent.message_id)
    await message.answer(i18n.t(lang, "giveaway_created", gid=gid))


@router.message(Command("stats"))
async def cmd_stats(message: Message, bot, db: Database, config: Config):
    lang = _lang(message)
    if not _require_admin(message, config):
        await message.answer(i18n.t(lang, "admin_only"))
        return

    giveaway = await db.latest_active_giveaway(message.chat.id) or await db.latest_active_giveaway()
    if giveaway is None:
        await message.answer(i18n.t(lang, "no_active"))
        return
    gid = int(giveaway["id"])
    parts = await db.count_participants(gid)
    refs = await db.count_all_referrals(gid)
    await message.answer(
        i18n.t(
            lang, "stats",
            gid=gid, prize=escape(giveaway["prize"]), status=giveaway["status"],
            parts=parts, refs=refs, ends=str(giveaway["ends_at"]), seed=giveaway["seed"],
        )
    )


@router.message(Command("participants"))
async def cmd_participants(message: Message, bot, db: Database, config: Config):
    lang = _lang(message)
    if not _require_admin(message, config):
        await message.answer(i18n.t(lang, "admin_only"))
        return
    giveaway = await db.latest_active_giveaway(message.chat.id) or await db.latest_active_giveaway()
    if giveaway is None:
        await message.answer(i18n.t(lang, "no_active"))
        return
    gid = int(giveaway["id"])
    rows = await db.list_participants(gid)
    header = i18n.t(lang, "list_header", gid=gid, count=len(rows))
    lines = []
    for r in rows:
        name = r.get("username") or r.get("full_name") or r["user_id"]
        lines.append(f"• {escape(str(name))} (id {r['user_id']})")
    body = "\n".join(lines) if lines else "—"
    await message.answer(f"{header}\n{body}")


@router.message(Command("finish"))
async def cmd_finish(message: Message, bot, db: Database, config: Config):
    """Force-finish the latest active giveaway in this chat (admin only)."""
    lang = _lang(message)
    if not _require_admin(message, config):
        await message.answer(i18n.t(lang, "admin_only"))
        return
    giveaway = await db.latest_active_giveaway(message.chat.id) or await db.latest_active_giveaway()
    if giveaway is None:
        await message.answer(i18n.t(lang, "no_active"))
        return
    await run_draw(bot, db, giveaway)
