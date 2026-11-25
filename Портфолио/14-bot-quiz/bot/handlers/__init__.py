"""Handler routers.

Registration order matters: the admin router owns the ``/addquestion`` FSM and
must see its command messages first, so it is included before the generic
routers. The poll-answer router only handles poll updates and is independent.
"""
from __future__ import annotations

from aiogram import Dispatcher

from . import admin, common, player, polls


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(admin.router)
    dp.include_router(player.router)
    dp.include_router(common.router)
    dp.include_router(polls.router)


__all__ = ["register_handlers", "admin", "common", "player", "polls"]
