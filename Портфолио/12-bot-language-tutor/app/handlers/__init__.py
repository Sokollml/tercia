"""Handler routers, assembled into a single aiogram :class:`Router`.

The submodules register their handlers on module-level routers; :func:`build_router`
wires them together in priority order (onboarding → quiz → stats → dialog).
Compatible with Python 3.9.
"""
from __future__ import annotations


def build_router():
    """Return a single aiogram Router with every feature router included."""
    from aiogram import Router

    from . import common, dialog, onboarding, quiz, stats

    root = Router(name="root")
    # Order matters: specific commands / states before the catch-all dialog.
    root.include_router(common.router)
    root.include_router(onboarding.router)
    root.include_router(quiz.router)
    root.include_router(stats.router)
    root.include_router(dialog.router)
    return root
