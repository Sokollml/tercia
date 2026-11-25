"""Welcome + captcha flow for newcomers."""
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message, User

from .. import i18n, utils
from ..keyboards import CAPTCHA_PREFIX, captcha_keyboard, parse_captcha_callback
from ..moderation import check_captcha, make_captcha, now_ts
from ..repository import Repository

log = logging.getLogger("moderation.handlers.captcha")
router = Router(name="captcha")


async def start_captcha(bot: Bot, repo: Repository, chat_id: int, chat_title: str, user: User) -> None:
    """Restrict a newcomer and post a captcha challenge with a deadline."""
    if user.is_bot:
        return
    row = await repo.ensure_chat(chat_id, chat_title)
    if not int(row.get("captcha_enabled") or 0):
        return
    lang = row.get("lang") or repo.cfg.default_lang
    timeout = int(row.get("captcha_timeout") or repo.cfg.captcha_timeout)

    if not await utils.bot_can_restrict(bot, chat_id):
        log.warning("captcha skipped: bot lacks restrict rights in chat %s", chat_id)
        return

    # Mute the newcomer until they solve (permanent restriction; lifted on pass
    # or replaced by the timeout kick).
    await utils.restrict_user(bot, chat_id, user.id, until_ts=0)

    captcha = make_captcha()
    deadline = now_ts() + timeout
    text = i18n.t(
        lang,
        "captcha_prompt",
        name=utils.mention(user),
        seconds=timeout,
        question=captcha.question,
    )
    sent: Optional[Message] = None
    try:
        sent = await bot.send_message(
            chat_id, text, reply_markup=captcha_keyboard(user.id, captcha)
        )
    except Exception as exc:  # pragma: no cover - network
        log.warning("failed to send captcha: %s", exc)

    message_id = sent.message_id if sent is not None else 0
    await repo.add_pending(chat_id, user.id, message_id, captcha.answer, deadline)
    await repo.log_action(chat_id, "captcha_issued", target_id=user.id)


@router.message(F.new_chat_members)
async def on_new_members(message: Message, bot: Bot, repo: Repository) -> None:
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    for member in message.new_chat_members or []:
        await start_captcha(bot, repo, message.chat.id, message.chat.title or "", member)


@router.chat_member()
async def on_chat_member(event: ChatMemberUpdated, bot: Bot, repo: Repository) -> None:
    """Catch joins that arrive as ChatMember updates (link joins in supergroups)."""
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    joined = old_status in ("left", "kicked") and new_status == "member"
    if not joined:
        return
    await start_captcha(bot, repo, event.chat.id, event.chat.title or "", event.new_chat_member.user)


@router.callback_query(F.data.startswith(CAPTCHA_PREFIX + ":"))
async def on_captcha_answer(callback: CallbackQuery, bot: Bot, repo: Repository) -> None:
    parsed = parse_captcha_callback(callback.data or "")
    if parsed is None:
        await callback.answer()
        return
    target_id, token = parsed
    chat = callback.message.chat if callback.message else None
    if chat is None:
        await callback.answer()
        return
    row = await repo.ensure_chat(chat.id, chat.title or "")
    lang = row.get("lang") or repo.cfg.default_lang

    # Only the challenged user may answer their own captcha.
    if callback.from_user.id != target_id:
        await callback.answer(i18n.t(lang, "captcha_not_yours"), show_alert=True)
        return

    pending = await repo.get_pending(chat.id, target_id)
    if pending is None:
        await callback.answer()
        return

    if check_captcha(pending["answer"], token):
        await repo.remove_pending(chat.id, target_id)
        await utils.unrestrict_user(bot, chat.id, target_id)
        await repo.log_action(chat.id, "captcha_pass", target_id=target_id)
        await callback.answer(i18n.t(lang, "captcha_pass", name=""))
        try:
            await callback.message.edit_text(
                i18n.t(lang, "captcha_pass", name=utils.display_name(callback.from_user))
            )
        except Exception:  # pragma: no cover - best effort
            pass
    else:
        await repo.remove_pending(chat.id, target_id)
        await utils.kick_user(bot, chat.id, target_id)
        await repo.log_action(chat.id, "captcha_fail", target_id=target_id)
        await callback.answer(i18n.t(lang, "captcha_fail_wrong"), show_alert=True)
        await utils.delete_message_safe(bot, chat.id, callback.message.message_id)
