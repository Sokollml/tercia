"""Reminder time calculation and 'due reminder' querying."""
from __future__ import annotations

import pytest

from app.services import (
    REMINDER_LEAD_SECONDS,
    now_ts,
    reminder_ts,
    should_schedule_reminder,
)

from .conftest import CLIENT_A, MASTER_ID

pytestmark_async = pytest.mark.asyncio


def test_reminder_is_one_hour_before():
    start = 1_700_000_000
    assert reminder_ts(start) == start - 3600
    assert REMINDER_LEAD_SECONDS == 3600


def test_should_schedule_when_far_in_future():
    start = now_ts() + 5 * 3600
    assert should_schedule_reminder(start) is True


def test_should_not_schedule_when_within_lead_window():
    # Appointment in 30 minutes -> reminder time already passed.
    start = now_ts() + 1800
    assert should_schedule_reminder(start) is False


def test_should_not_schedule_for_past_appointment():
    start = now_ts() - 100
    assert should_schedule_reminder(start) is False


@pytest.mark.asyncio
async def test_due_reminders_returns_appointment_within_the_hour(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    # Appointment in 40 minutes -> reminder is due now.
    start = now_ts() + 40 * 60
    slot_id = await repo.add_slot(MASTER_ID, start, start + 3600)
    await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())

    due = await repo.due_reminders(now_ts=now_ts(), horizon_ts=now_ts())
    assert len(due) == 1
    assert due[0]["client_id"] == CLIENT_A


@pytest.mark.asyncio
async def test_due_reminders_excludes_far_future(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    start = now_ts() + 5 * 3600  # 5 hours away -> not due
    slot_id = await repo.add_slot(MASTER_ID, start, start + 3600)
    await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())

    due = await repo.due_reminders(now_ts=now_ts(), horizon_ts=now_ts())
    assert due == []


@pytest.mark.asyncio
async def test_reminder_not_resent_after_marked(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    start = now_ts() + 40 * 60
    slot_id = await repo.add_slot(MASTER_ID, start, start + 3600)
    booking_id = await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())

    await repo.mark_reminder_sent(booking_id)
    due = await repo.due_reminders(now_ts=now_ts(), horizon_ts=now_ts())
    assert due == []
