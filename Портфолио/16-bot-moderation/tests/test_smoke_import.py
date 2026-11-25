"""Smoke test: every module imports cleanly (catches syntax / wiring errors)."""
from __future__ import annotations

import importlib

MODULES = [
    "app",
    "app.config",
    "app.db",
    "app.dbsetup",
    "app.repository",
    "app.moderation",
    "app.logger",
    "app.i18n",
    "app.keyboards",
    "app.utils",
    "app.middlewares",
    "app.scheduler",
    "app.bot",
    "app.handlers",
    "app.handlers.common",
    "app.handlers.captcha",
    "app.handlers.antispam",
    "app.handlers.commands",
    "app.handlers.settings",
]


def test_all_modules_import():
    for name in MODULES:
        importlib.import_module(name)


def test_build_router_assembles():
    from app.handlers import build_router

    router = build_router()
    assert router.sub_routers  # sub-routers attached
