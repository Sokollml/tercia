"""Bot-facing services that combine the DB, Telegram API and pure logic."""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from . import logic
from .db import Database

log = logging.getLogger(__name__)

# Statuses that mean "user is a member of the channel".
_MEMBER_STATUSES = {"creator", "administrator", "member", "owner"}


async def is_subscribed(bot: Bot, channel: Optional[str], user_id: int) -> bool:
    """Check channel membership via get_chat_member.

    If no channel is required -> always True. On API errors (e.g. the bot is
    not an admin of the channel) we fail-open=False, i.e. treat as not
    subscribed, and log the problem so the admin can fix permissions.
    """
    if not channel:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in _MEMBER_STATUSES
    except TelegramAPIError as exc:
        log.warning("get_chat_member failed for %s in %s: %s", user_id, channel, exc)
        return False


async def run_draw(bot: Bot, db: Database, giveaway: dict) -> List[int]:
    """Finish a giveaway: compute winners deterministically, persist, announce.

    Returns the list of winner user_ids (possibly empty).
    """
    gid = int(giveaway["id"])
    seed = giveaway["seed"]
    winners_count = int(giveaway["winners_count"])
    points_per_ref = int(giveaway["points_per_ref"])

    pool = await db.participants_with_tickets(gid, points_per_ref)
    winners = logic.select_winners(pool, seed, winners_count)

    await db.finish_giveaway(gid, winners)

    parts = len(pool)
    prize = giveaway["prize"]
    lang = "ru"  # announcements go to the community in the default language

    from . import i18n  # local import to avoid cycles

    if winners:
        winners_text = "\n".join(f"• <a href=\"tg://user?id={w}\">{w}</a>" for w in winners)
        text = i18n.t(
            lang, "winners_announce",
            prize=prize, winners=winners_text, seed=seed, parts=parts,
        )
    else:
        text = i18n.t(lang, "winners_none", prize=prize)

    try:
        await bot.send_message(chat_id=int(giveaway["chat_id"]), text=text)
    except TelegramAPIError as exc:
        log.error("failed to announce winners for giveaway %s: %s", gid, exc)

    log.info("giveaway %s finished, winners=%s seed=%s", gid, winners, seed)
    return winners
