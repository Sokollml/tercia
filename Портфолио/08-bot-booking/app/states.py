"""FSM state groups for the booking scenario.

Kept in a dedicated module so the flow is easy to read and to unit-test
without importing any handler / bot machinery.

Client booking flow:
    choosing_service -> choosing_slot -> confirming -> (done)
"""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class BookingFlow(StatesGroup):
    """States a client passes through while making a booking."""

    choosing_service = State()
    choosing_slot = State()
    confirming = State()


class MasterFlow(StatesGroup):
    """States for master-side actions that need multiple steps."""

    adding_slot = State()


# Ordered client flow — used by tests and by handlers to validate transitions.
BOOKING_ORDER = (
    BookingFlow.choosing_service,
    BookingFlow.choosing_slot,
    BookingFlow.confirming,
)


def next_state(current: State) -> State | None:
    """Return the state that follows ``current`` in the booking flow.

    Returns ``None`` when ``current`` is the last state (or unknown).
    """
    try:
        idx = BOOKING_ORDER.index(current)
    except ValueError:
        return None
    if idx + 1 >= len(BOOKING_ORDER):
        return None
    return BOOKING_ORDER[idx + 1]
