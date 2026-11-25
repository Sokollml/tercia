-- PostgreSQL schema for the AI language-tutor bot (production).
-- Timestamps are UNIX epoch seconds (UTC), stored as BIGINT.

CREATE TABLE IF NOT EXISTS users (
    id            BIGINT  PRIMARY KEY,          -- telegram user id
    ui_lang       TEXT    NOT NULL DEFAULT 'ru',
    learn_lang    TEXT,
    level         TEXT,
    is_premium    BOOLEAN NOT NULL DEFAULT FALSE,
    daily_date    TEXT,
    daily_count   INTEGER NOT NULL DEFAULT 0,
    created_at    BIGINT  NOT NULL
);

CREATE TABLE IF NOT EXISTS mistakes (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT  NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    original      TEXT    NOT NULL,
    corrected     TEXT    NOT NULL,
    explanation   TEXT    NOT NULL DEFAULT '',
    error_type    TEXT    NOT NULL DEFAULT 'other',
    repetitions   INTEGER NOT NULL DEFAULT 0,
    interval_days INTEGER NOT NULL DEFAULT 0,
    ease          DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    next_review   BIGINT  NOT NULL,
    times_correct INTEGER NOT NULL DEFAULT 0,
    times_wrong   INTEGER NOT NULL DEFAULT 0,
    last_reviewed BIGINT,
    created_at    BIGINT  NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mistakes_user_due
    ON mistakes (user_id, next_review);

CREATE TABLE IF NOT EXISTS sessions (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT  NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    mode          TEXT    NOT NULL,
    messages      INTEGER NOT NULL DEFAULT 0,
    started_at    BIGINT  NOT NULL,
    ended_at      BIGINT
);

CREATE INDEX IF NOT EXISTS idx_sessions_user
    ON sessions (user_id, started_at);
