-- SQLite schema for the AI language-tutor bot (local development).
-- Timestamps are UNIX epoch seconds (UTC).

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,          -- telegram user id
    ui_lang       TEXT    NOT NULL DEFAULT 'ru',-- interface language (ru/en)
    learn_lang    TEXT,                         -- language being learned (en/de/...)
    level         TEXT,                         -- CEFR level (A1..C1)
    is_premium    INTEGER NOT NULL DEFAULT 0,   -- 0 = free tier (daily limit applies)
    daily_date    TEXT,                         -- YYYY-MM-DD the counter belongs to
    daily_count   INTEGER NOT NULL DEFAULT 0,   -- corrections used today
    created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS mistakes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    original      TEXT    NOT NULL,             -- what the learner wrote
    corrected     TEXT    NOT NULL,             -- the corrected form
    explanation   TEXT    NOT NULL DEFAULT '',  -- learner-facing explanation
    error_type    TEXT    NOT NULL DEFAULT 'other',
    repetitions   INTEGER NOT NULL DEFAULT 0,   -- SRS success streak
    interval_days INTEGER NOT NULL DEFAULT 0,   -- current spacing (days)
    ease          REAL    NOT NULL DEFAULT 2.5, -- SM-2 ease factor
    next_review   INTEGER NOT NULL,             -- epoch of next scheduled review
    times_correct INTEGER NOT NULL DEFAULT 0,
    times_wrong   INTEGER NOT NULL DEFAULT 0,
    last_reviewed INTEGER,
    created_at    INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mistakes_user_due
    ON mistakes (user_id, next_review);

CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    mode          TEXT    NOT NULL,             -- 'dialog' | 'quiz'
    messages      INTEGER NOT NULL DEFAULT 0,
    started_at    INTEGER NOT NULL,
    ended_at      INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user
    ON sessions (user_id, started_at);
