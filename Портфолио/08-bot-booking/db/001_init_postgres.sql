-- PostgreSQL schema (production).
-- Timestamps are stored as UNIX epoch seconds (BIGINT, UTC).
-- Flags use SMALLINT 0/1 so the application SQL is identical across drivers.

CREATE TABLE IF NOT EXISTS masters (
    id          BIGINT PRIMARY KEY,           -- telegram user id
    name        TEXT     NOT NULL,
    tz          TEXT     NOT NULL DEFAULT 'Europe/Moscow',
    created_at  BIGINT   NOT NULL
);

CREATE TABLE IF NOT EXISTS services (
    id            BIGSERIAL PRIMARY KEY,
    master_id     BIGINT   NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
    title         TEXT     NOT NULL,
    duration_min  INTEGER  NOT NULL DEFAULT 60,
    price         TEXT     NOT NULL DEFAULT '',
    is_active     SMALLINT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS slots (
    id          BIGSERIAL PRIMARY KEY,
    master_id   BIGINT   NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
    start_ts    BIGINT   NOT NULL,            -- epoch seconds
    end_ts      BIGINT   NOT NULL,
    is_closed   SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookings (
    id             BIGSERIAL PRIMARY KEY,
    slot_id        BIGINT   NOT NULL REFERENCES slots(id) ON DELETE CASCADE,
    service_id     BIGINT   NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    client_id      BIGINT   NOT NULL,         -- telegram user id
    client_name    TEXT     NOT NULL DEFAULT '',
    status         TEXT     NOT NULL DEFAULT 'confirmed',  -- confirmed | cancelled
    reminder_sent  SMALLINT NOT NULL DEFAULT 0,
    created_at     BIGINT   NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_slots_master_start ON slots(master_id, start_ts);
CREATE INDEX IF NOT EXISTS idx_bookings_slot ON bookings(slot_id);
CREATE INDEX IF NOT EXISTS idx_bookings_client ON bookings(client_id);

-- Guard: at most one confirmed booking per slot.
CREATE UNIQUE INDEX IF NOT EXISTS uq_booking_slot_confirmed
    ON bookings(slot_id) WHERE status = 'confirmed';
