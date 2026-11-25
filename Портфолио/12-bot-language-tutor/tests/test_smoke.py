"""Smoke test: every module imports cleanly (catches syntax / wiring errors).

Importing the handler package and ``app.bot`` also pulls in aiogram, so this
doubles as a check that the runtime wiring is consistent.
"""
from __future__ import annotations

import importlib

import pytest

PURE_MODULES = [
    "app",
    "app.config",
    "app.db",
    "app.llm",
    "app.logger",
    "app.repository",
    "app.services",
    "app.srs",
    "app.i18n",
    "app.states",
    "app.middlewares",
]

RUNTIME_MODULES = [
    "app.keyboards",
    "app.scheduler",
    "app.handlers",
    "app.handlers.common",
    "app.handlers.onboarding",
    "app.handlers.dialog",
    "app.handlers.quiz",
    "app.handlers.stats",
    "app.bot",
]


@pytest.mark.parametrize("name", PURE_MODULES)
def test_pure_modules_import(name):
    assert importlib.import_module(name) is not None


@pytest.mark.parametrize("name", RUNTIME_MODULES)
def test_runtime_modules_import(name):
    # These need aiogram; skip cleanly if it's not installed rather than fail.
    pytest.importorskip("aiogram")
    assert importlib.import_module(name) is not None


def test_build_router_constructs():
    pytest.importorskip("aiogram")
    from app.handlers import build_router

    router = build_router()
    assert router is not None


def test_config_factory_and_languages():
    from app.config import LEARN_LANGUAGES, LEVELS, load_config

    cfg = load_config()
    assert cfg.db_driver in {"sqlite", "postgres"}
    assert "en" in LEARN_LANGUAGES
    assert "A1" in LEVELS
