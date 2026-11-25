"""Router registration."""
from __future__ import annotations

from aiogram import Dispatcher

from bot.handlers import admin, commands, members, messages


def register_handlers(dp: Dispatcher) -> None:
    # order matters: commands & members before the catch-all message handler
    dp.include_router(members.router)
    dp.include_router(commands.router)
    dp.include_router(admin.router)
    dp.include_router(messages.router)
