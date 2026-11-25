-- SQLite schema (local development / tests).
-- Timestamps are stored as UNIX epoch seconds (INTEGER, UTC).
-- Boolean-ish flags use INTEGER 0/1 to stay uniform with the Postgres schema.

CREATE TABLE IF NOT EXISTS masters (
    id          INTEGER PRIMARY KEY,          -- telegram user id
    name        TEXT    NOT NULL,
    tz          TEXT    NOT NULL DEFAULT 'Europe/Moscow',
    created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS services (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id     INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
    title         TEXT    NOT NULL,
    duration_min  INTEGER NOT NULL DEFAULT 60,
    price         TEXT    NOT NULL DEFAULT '',
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS slots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id   INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
    start_ts    INTEGER NOT NULL,             -- epoch seconds
    end_ts      INTEGER NOT NULL,
    is_closed   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id        INTEGER NOT NULL REFERENCES slots(id) ON DELETE CASCADE,
    service_id     INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    client_id      INTEGER NOT NULL,          -- telegram user id
    client_name    TEXT    NOT NULL DEFAULT '',
    status         TEXT    NOT NULL DEFAULT 'confirmed',  -- confirmed | cancelled
    reminder_sent  INTEGER NOT NULL DEFAULT 0,
    created_at     INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_slots_master_start ON slots(master_id, start_ts);
CREATE INDEX IF NOT EXISTS idx_bookings_slot ON bookings(slot_id);
CREATE INDEX IF NOT EXISTS idx_bookings_client ON bookings(client_id);

-- Guard: at most one confirmed booking per slot.
CREATE UNIQUE INDEX IF NOT EXISTS uq_booking_slot_confirmed
    ON bookings(slot_id) WHERE status = 'confirmed';
