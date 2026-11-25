"""Data-access layer: all SQL lives here, driver-agnostic.

The repository speaks the small :class:`app.db.Database` API and returns plain
dicts, keeping handlers and tests free of SQL.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .db import Database


class SlotUnavailableError(Exception):
    """Raised when a booking cannot be created because the slot is taken/closed."""


class Repository:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ---- masters ---------------------------------------------------------
    async def upsert_master(self, master_id: int, name: str, tz: str, created_at: int) -> None:
        existing = await self.db.fetchone("SELECT id FROM masters WHERE id = ?", master_id)
        if existing is None:
            await self.db.execute(
                "INSERT INTO masters (id, name, tz, created_at) VALUES (?, ?, ?, ?)",
                master_id,
                name,
                tz,
                created_at,
            )

    async def get_master(self, master_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM masters WHERE id = ?", master_id)

    async def any_master_id(self) -> Optional[int]:
        row = await self.db.fetchone("SELECT id FROM masters ORDER BY id LIMIT 1")
        return int(row["id"]) if row else None

    # ---- services --------------------------------------------------------
    async def add_service(
        self, master_id: int, title: str, duration_min: int, price: str
    ) -> int:
        return await self.db.insert(
            "INSERT INTO services (master_id, title, duration_min, price, is_active) "
            "VALUES (?, ?, ?, ?, 1) RETURNING id",
            master_id,
            title,
            duration_min,
            price,
        )

    async def list_services(self, master_id: int) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT * FROM services WHERE master_id = ? AND is_active = 1 ORDER BY id",
            master_id,
        )

    async def get_service(self, service_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM services WHERE id = ?", service_id)

    # ---- slots -----------------------------------------------------------
    async def add_slot(self, master_id: int, start_ts: int, end_ts: int) -> int:
        return await self.db.insert(
            "INSERT INTO slots (master_id, start_ts, end_ts, is_closed) "
            "VALUES (?, ?, ?, 0) RETURNING id",
            master_id,
            start_ts,
            end_ts,
        )

    async def get_slot(self, slot_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM slots WHERE id = ?", slot_id)

    async def is_slot_free(self, slot_id: int) -> bool:
        row = await self.db.fetchone(
            "SELECT s.id FROM slots s "
            "WHERE s.id = ? AND s.is_closed = 0 "
            "AND NOT EXISTS (SELECT 1 FROM bookings b WHERE b.slot_id = s.id AND b.status = 'confirmed')",
            slot_id,
        )
        return row is not None

    async def list_free_slots(self, master_id: int, from_ts: int) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT s.* FROM slots s "
            "WHERE s.master_id = ? AND s.is_closed = 0 AND s.start_ts >= ? "
            "AND NOT EXISTS (SELECT 1 FROM bookings b WHERE b.slot_id = s.id AND b.status = 'confirmed') "
            "ORDER BY s.start_ts",
            master_id,
            from_ts,
        )

    async def close_slot(self, slot_id: int) -> None:
        await self.db.execute("UPDATE slots SET is_closed = 1 WHERE id = ?", slot_id)

    async def list_slots_between(
        self, master_id: int, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT * FROM slots WHERE master_id = ? AND start_ts >= ? AND start_ts < ? "
            "ORDER BY start_ts",
            master_id,
            start_ts,
            end_ts,
        )

    # ---- bookings --------------------------------------------------------
    async def create_booking(
        self, slot_id: int, service_id: int, client_id: int, client_name: str, created_at: int
    ) -> int:
        """Create a confirmed booking or raise :class:`SlotUnavailableError`."""
        inserted, booking_id = await self.db.try_book(
            slot_id, service_id, client_id, client_name, created_at
        )
        if not inserted or booking_id is None:
            raise SlotUnavailableError(slot_id)
        return booking_id

    async def get_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone("SELECT * FROM bookings WHERE id = ?", booking_id)

    async def get_booking_full(self, booking_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.fetchone(
            "SELECT b.*, s.start_ts, s.end_ts, sv.title AS service_title, sv.price AS price "
            "FROM bookings b "
            "JOIN slots s ON s.id = b.slot_id "
            "JOIN services sv ON sv.id = b.service_id "
            "WHERE b.id = ?",
            booking_id,
        )

    async def list_client_bookings(self, client_id: int, from_ts: int) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT b.id, b.status, s.start_ts, sv.title AS service_title "
            "FROM bookings b "
            "JOIN slots s ON s.id = b.slot_id "
            "JOIN services sv ON sv.id = b.service_id "
            "WHERE b.client_id = ? AND b.status = 'confirmed' AND s.start_ts >= ? "
            "ORDER BY s.start_ts",
            client_id,
            from_ts,
        )

    async def cancel_booking(self, booking_id: int) -> None:
        await self.db.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?", booking_id
        )

    async def bookings_for_day(
        self, master_id: int, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        return await self.db.fetchall(
            "SELECT b.id, b.client_id, b.client_name, s.start_ts, s.end_ts, sv.title AS service_title "
            "FROM bookings b "
            "JOIN slots s ON s.id = b.slot_id "
            "JOIN services sv ON sv.id = b.service_id "
            "WHERE s.master_id = ? AND b.status = 'confirmed' "
            "AND s.start_ts >= ? AND s.start_ts < ? "
            "ORDER BY s.start_ts",
            master_id,
            start_ts,
            end_ts,
        )

    # ---- reminders -------------------------------------------------------
    async def due_reminders(self, now_ts: int, horizon_ts: int) -> List[Dict[str, Any]]:
        """Confirmed bookings whose reminder time falls in (now, horizon] and
        which have not been reminded yet."""
        return await self.db.fetchall(
            "SELECT b.id, b.client_id, s.start_ts, sv.title AS service_title "
            "FROM bookings b "
            "JOIN slots s ON s.id = b.slot_id "
            "JOIN services sv ON sv.id = b.service_id "
            "WHERE b.status = 'confirmed' AND b.reminder_sent = 0 "
            "AND (s.start_ts - 3600) <= ? AND s.start_ts > ? "
            "ORDER BY s.start_ts",
            horizon_ts,
            now_ts,
        )

    async def mark_reminder_sent(self, booking_id: int) -> None:
        await self.db.execute(
            "UPDATE bookings SET reminder_sent = 1 WHERE id = ?", booking_id
        )
