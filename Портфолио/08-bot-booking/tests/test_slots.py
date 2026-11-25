"""Slot availability: you cannot book an already-booked or closed slot."""
from __future__ import annotations

import pytest

from app.repository import SlotUnavailableError
from app.services import now_ts

from .conftest import CLIENT_A, CLIENT_B, MASTER_ID

pytestmark = pytest.mark.asyncio


async def _make_slot(repo, offset=3600):
    start = now_ts() + offset
    return await repo.add_slot(MASTER_ID, start, start + 3600)


async def test_free_slot_can_be_booked(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    slot_id = await _make_slot(repo)

    assert await repo.is_slot_free(slot_id) is True
    booking_id = await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())
    assert booking_id > 0
    assert await repo.is_slot_free(slot_id) is False


async def test_cannot_book_taken_slot(repo):
    """The core rule: a second client cannot grab a confirmed slot."""
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    slot_id = await _make_slot(repo)

    await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())

    with pytest.raises(SlotUnavailableError):
        await repo.create_booking(slot_id, service_id, CLIENT_B, "B", now_ts())


async def test_cannot_book_closed_slot(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    slot_id = await _make_slot(repo)

    await repo.close_slot(slot_id)
    assert await repo.is_slot_free(slot_id) is False

    with pytest.raises(SlotUnavailableError):
        await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())


async def test_cancelled_booking_frees_the_slot(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    slot_id = await _make_slot(repo)

    booking_id = await repo.create_booking(slot_id, service_id, CLIENT_A, "A", now_ts())
    await repo.cancel_booking(booking_id)

    assert await repo.is_slot_free(slot_id) is True
    # Another client can now take it.
    new_id = await repo.create_booking(slot_id, service_id, CLIENT_B, "B", now_ts())
    assert new_id > 0


async def test_free_slots_listing_excludes_booked_and_closed(repo):
    service_id = await repo.add_service(MASTER_ID, "Haircut", 45, "25")
    s1 = await _make_slot(repo, offset=3600)
    s2 = await _make_slot(repo, offset=7200)
    s3 = await _make_slot(repo, offset=10800)

    await repo.create_booking(s1, service_id, CLIENT_A, "A", now_ts())
    await repo.close_slot(s2)

    free = await repo.list_free_slots(MASTER_ID, now_ts())
    free_ids = {row["id"] for row in free}
    assert free_ids == {s3}
