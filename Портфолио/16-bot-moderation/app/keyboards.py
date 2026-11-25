"""Inline keyboards."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .moderation import Captcha

# Callback payload: captcha:<user_id>:<token>
CAPTCHA_PREFIX = "captcha"


def captcha_keyboard(user_id: int, captcha: Captcha) -> InlineKeyboardMarkup:
    """Buttons for a newcomer captcha, bound to the target user's id."""
    row = [
        InlineKeyboardButton(
            text=opt,
            callback_data="%s:%d:%s" % (CAPTCHA_PREFIX, user_id, opt),
        )
        for opt in captcha.options
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def parse_captcha_callback(data: str):
    """Return ``(user_id, token)`` from callback data, or ``None`` if malformed."""
    parts = (data or "").split(":", 2)
    if len(parts) != 3 or parts[0] != CAPTCHA_PREFIX:
        return None
    try:
        return int(parts[1]), parts[2]
    except ValueError:
        return None
