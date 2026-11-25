"""Handler routers, exported in registration order.

Order matters: command routers must be registered before the catch-all
antispam handler so slash commands are not treated as regular messages.
"""
from __future__ import annotations

from aiogram import Router

from . import antispam, captcha, commands, common, settings


def build_router() -> Router:
    """Assemble a single root router with all sub-routers attached."""
    root = Router(name="root")
    root.include_router(common.router)
    root.include_router(captcha.router)
    root.include_router(commands.router)
    root.include_router(settings.router)
    # Antispam last — it catches ordinary group messages.
    root.include_router(antispam.router)
    return root


__all__ = ["build_router"]
