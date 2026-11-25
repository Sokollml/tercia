"""FSM transition correctness for the booking flow."""
from __future__ import annotations

from app.states import BOOKING_ORDER, BookingFlow, next_state


def test_booking_order_is_service_slot_confirm():
    assert BOOKING_ORDER == (
        BookingFlow.choosing_service,
        BookingFlow.choosing_slot,
        BookingFlow.confirming,
    )


def test_transitions_follow_the_flow():
    assert next_state(BookingFlow.choosing_service) == BookingFlow.choosing_slot
    assert next_state(BookingFlow.choosing_slot) == BookingFlow.confirming


def test_last_state_has_no_next():
    assert next_state(BookingFlow.confirming) is None


def test_unknown_state_returns_none():
    assert next_state(None) is None


def test_states_are_distinct():
    names = {
        BookingFlow.choosing_service.state,
        BookingFlow.choosing_slot.state,
        BookingFlow.confirming.state,
    }
    assert len(names) == 3
