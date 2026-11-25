"""Moderation commands: /warn /mute /unmute /ban /unban /kick /warns /log."""
from __future__ import annotations

import logging
from typing import Optional, Tuple

from aiogram import Bot, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, User

from .. import i18n, utils
from ..moderation import format_duration, now_ts, should_mute
from ..repository import Repository

log = logging.getLogger("moderation.handlers.commands")
router = Router(name="commands")


def _target(message: Message) -> Optional[User]:
    """The user a reply-based command targets, or None."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


async def _guard(message: Message, bot: Bot, repo: Repository) -> Optional[str]:
    """Common checks. Returns the chat language on success, None if blocked.

    Sends the appropriate error message itself when a check fails.
    """
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return None
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    if not await utils.is_user_admin(bot, repo.cfg, message.chat.id, message.from_user.id):
        await message.answer(i18n.t(lang, "not_admin"))
        return None
    if not await utils.bot_can_restrict(bot, message.chat.id):
        await message.answer(i18n.t(lang, "bot_not_admin"))
        return None
    return lang


async def _require_target(message: Message, bot: Bot, repo: Repository, lang: str) -> Optional[User]:
    target = _target(message)
    if target is None:
        await message.answer(i18n.t(lang, "reply_required"))
        return None
    if await utils.is_user_admin(bot, repo.cfg, message.chat.id, target.id):
        await message.answer(i18n.t(lang, "cant_target_admin"))
        return None
    return target


def _split_minutes(args: Optional[str]) -> Tuple[Optional[int], str]:
    """Parse an optional leading '<minutes>' from command args.

    Returns ``(minutes_or_None, remaining_reason)``.
    """
    args = (args or "").strip()
    if not args:
        return None, ""
    first, _, rest = args.partition(" ")
    if first.isdigit():
        return int(first), rest.strip()
    return None, args


@router.message(Command("warn"))
async def cmd_warn(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = await _require_target(message, bot, repo, lang)
    if target is None:
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    warn_limit = int(row.get("warn_limit") or repo.cfg.warn_limit)
    mute_duration = int(row.get("mute_duration") or repo.cfg.mute_duration)
    reason = (command.args or "").strip() or i18n.t(lang, "no_reason")

    await repo.add_warning(message.chat.id, target.id, message.from_user.id, reason)
    count = await repo.count_active_warnings(message.chat.id, target.id)
    await repo.log_action(
        message.chat.id, "warn", actor_id=message.from_user.id, target_id=target.id, details=reason
    )

    if should_mute(count, warn_limit):
        until = now_ts() + mute_duration
        await utils.restrict_user(bot, message.chat.id, target.id, until_ts=until)
        await repo.add_mute(message.chat.id, target.id, until, admin_id=0, reason="warn_limit")
        await repo.reset_warnings(message.chat.id, target.id)
        await repo.log_action(
            message.chat.id, "warn_mute", actor_id=0, target_id=target.id
        )
        await message.answer(
            i18n.t(
                lang,
                "warn_muted",
                name=utils.mention(target),
                count=count,
                duration=format_duration(mute_duration, lang),
            )
        )
    else:
        await message.answer(
            i18n.t(
                lang,
                "warn_issued",
                name=utils.mention(target),
                count=count,
                limit=warn_limit,
                reason=reason,
            )
        )


@router.message(Command("mute"))
async def cmd_mute(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = await _require_target(message, bot, repo, lang)
    if target is None:
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    minutes, reason = _split_minutes(command.args)
    duration = minutes * 60 if minutes else int(row.get("mute_duration") or repo.cfg.mute_duration)
    reason = reason or i18n.t(lang, "no_reason")
    until = now_ts() + duration
    await utils.restrict_user(bot, message.chat.id, target.id, until_ts=until)
    await repo.add_mute(message.chat.id, target.id, until, admin_id=message.from_user.id, reason=reason)
    await repo.log_action(
        message.chat.id, "mute", actor_id=message.from_user.id, target_id=target.id, details=reason
    )
    await message.answer(
        i18n.t(
            lang,
            "mute_issued",
            name=utils.mention(target),
            duration=format_duration(duration, lang),
            reason=reason,
        )
    )


@router.message(Command("unmute"))
async def cmd_unmute(message: Message, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = _target(message)
    if target is None:
        await message.answer(i18n.t(lang, "reply_required"))
        return
    await utils.unrestrict_user(bot, message.chat.id, target.id)
    await repo.deactivate_mute(message.chat.id, target.id)
    await repo.log_action(
        message.chat.id, "unmute", actor_id=message.from_user.id, target_id=target.id
    )
    await message.answer(i18n.t(lang, "unmute_done", name=utils.mention(target)))


@router.message(Command("ban"))
async def cmd_ban(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = await _require_target(message, bot, repo, lang)
    if target is None:
        return
    reason = (command.args or "").strip() or i18n.t(lang, "no_reason")
    await utils.ban_user(bot, message.chat.id, target.id)
    await repo.log_action(
        message.chat.id, "ban", actor_id=message.from_user.id, target_id=target.id, details=reason
    )
    await message.answer(i18n.t(lang, "ban_issued", name=utils.mention(target), reason=reason))


@router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = _target(message)
    user_id = target.id if target else None
    if user_id is None:
        arg = (command.args or "").strip()
        if arg.lstrip("-").isdigit():
            user_id = int(arg)
    if user_id is None:
        await message.answer(i18n.t(lang, "unban_usage"))
        return
    await utils.unban_user(bot, message.chat.id, user_id)
    await repo.log_action(
        message.chat.id, "unban", actor_id=message.from_user.id, target_id=user_id
    )
    await message.answer(i18n.t(lang, "unban_done", user_id=user_id))


@router.message(Command("kick"))
async def cmd_kick(message: Message, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    target = await _require_target(message, bot, repo, lang)
    if target is None:
        return
    await utils.kick_user(bot, message.chat.id, target.id)
    await repo.log_action(
        message.chat.id, "kick", actor_id=message.from_user.id, target_id=target.id
    )
    await message.answer(i18n.t(lang, "kick_done", name=utils.mention(target)))


@router.message(Command("warns"))
async def cmd_warns(message: Message, bot: Bot, repo: Repository) -> None:
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    row = await repo.ensure_chat(message.chat.id, message.chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang
    target = _target(message) or message.from_user
    count = await repo.count_active_warnings(message.chat.id, target.id)
    await message.answer(
        i18n.t(
            lang,
            "warns_count",
            name=utils.mention(target),
            count=count,
            limit=int(row.get("warn_limit") or repo.cfg.warn_limit),
        )
    )


@router.message(Command("log"))
async def cmd_log(message: Message, bot: Bot, repo: Repository) -> None:
    lang = await _guard(message, bot, repo)
    if lang is None:
        return
    actions = await repo.recent_actions(message.chat.id, limit=10)
    if not actions:
        await message.answer(i18n.t(lang, "log_empty"))
        return
    lines = [i18n.t(lang, "log_header")]
    for a in actions:
        lines.append(
            "• %s | actor=%s | target=%s | %s"
            % (a["action"], a["actor_id"], a["target_id"], a.get("details") or "")
        )
    await message.answer("\n".join(lines))
