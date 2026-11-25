"""Public commands: /start /help /me /top /rank."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.i18n import t
from bot.services.leaderboard import alltime_top, member_position, weekly_top
from bot.services.members import get_or_create_chat, get_or_create_member
from bot.xp import RANKS, level_for_xp, rank_for_level, xp_threshold, xp_to_next_level

router = Router(name="commands")


def _medal(pos: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, f"{pos}.")


@router.message(Command("start", "help"))
async def cmd_help(message: Message, session: AsyncSession) -> None:
    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    await message.answer(t("help", chat.lang))


@router.message(Command("me"))
async def cmd_me(message: Message, session: AsyncSession) -> None:
    if message.chat.type not in ("group", "supergroup"):
        await message.answer(t("group_only", "ru"))
        return
    user = message.from_user
    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    member = await get_or_create_member(
        session, chat.id, user.id, user.username or "", user.full_name or ""
    )
    lang = chat.lang
    level = level_for_xp(member.xp)
    position = await member_position(session, chat.id, user.id)
    name = (f"@{user.username}" if user.username else user.full_name) or str(user.id)
    await message.answer(
        t(
            "me_card",
            lang,
            name=name,
            rank=rank_for_level(level, lang),
            level=level,
            xp=member.xp,
            to_next=xp_to_next_level(member.xp),
            streak=member.streak,
            position=position or 1,
        )
    )


@router.message(Command("top"))
async def cmd_top(message: Message, session: AsyncSession) -> None:
    if message.chat.type not in ("group", "supergroup"):
        await message.answer(t("group_only", "ru"))
        return
    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    lang = chat.lang

    week = await weekly_top(session, chat.id, limit=10)
    alltime = await alltime_top(session, chat.id, limit=10)

    lines = [t("top_header_week", lang)]
    if week:
        lines += [f"{_medal(r.position)} {r.name} — {r.value} XP" for r in week]
    else:
        lines.append(t("top_empty", lang))

    lines.append("")
    lines.append(t("top_header_all", lang))
    if alltime:
        lines += [f"{_medal(r.position)} {r.name} — {r.value} XP" for r in alltime]
    else:
        lines.append(t("top_empty", lang))

    await message.answer("\n".join(lines))


@router.message(Command("rank"))
async def cmd_rank(message: Message, session: AsyncSession) -> None:
    chat = await get_or_create_chat(session, message.chat.id, message.chat.title or "")
    lang = chat.lang
    lines = [t("ranks_table", lang)]
    for min_level, ru, en in RANKS:
        name = ru if lang == "ru" else en
        need = xp_threshold(min_level)
        lines.append(f"• {name} — уровень {min_level}+ ({need} XP)" if lang == "ru"
                     else f"• {name} — level {min_level}+ ({need} XP)")
    await message.answer("\n".join(lines))
