"""FSM state groups for the onboarding, dialog and quiz flows.

aiogram is imported lazily-tolerantly: if it is not installed (e.g. in a minimal
test environment) we fall back to a tiny stand-in so importing this module — and
therefore the whole ``app`` package — never fails.  Compatible with Python 3.9.
"""
from __future__ import annotations

try:
    from aiogram.fsm.state import State, StatesGroup
except Exception:  # pragma: no cover - exercised only without aiogram installed
    class State:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            self._name = None

        def __set_name__(self, owner, name) -> None:
            self._name = "{}:{}".format(owner.__name__, name)

        @property
        def state(self):
            return self._name

    class StatesGroup:  # type: ignore[no-redef]
        pass


class Onboarding(StatesGroup):
    """Choosing UI language, target language and CEFR level."""

    ui_lang = State()
    learn_lang = State()
    level = State()


class Dialog(StatesGroup):
    """Free conversation with live correction."""

    chatting = State()


class Quiz(StatesGroup):
    """Spaced-repetition review session."""

    answering = State()
