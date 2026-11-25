"""Handler routers."""
from __future__ import annotations

from aiogram import Router

from . import client, master


def build_router() -> Router:
    """Combine all feature routers into one."""
    root = Router(name="root")
    root.include_router(master.router)
    root.include_router(client.router)
    return root
