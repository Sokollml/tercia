"""Handler routers aggregation."""

from __future__ import annotations

from aiogram import Router

from . import admin, participant


def build_router() -> Router:
    router = Router()
    router.include_router(admin.router)
    router.include_router(participant.router)
    return router
