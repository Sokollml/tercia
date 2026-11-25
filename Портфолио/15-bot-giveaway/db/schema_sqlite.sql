-- SQLite schema (local development). Mirrors db/schema.sql.

CREATE TABLE IF NOT EXISTS giveaways (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         INTEGER NOT NULL,
    creator_id      INTEGER NOT NULL,
    prize           TEXT    NOT NULL,
    description     TEXT,
    winners_count   INTEGER NOT NULL DEFAULT 1,
    points_per_ref  INTEGER NOT NULL DEFAULT 1,
    required_channel TEXT,
    seed            TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'active',
    ends_at         TEXT    NOT NULL,              -- ISO-8601 UTC
    announce_msg_id INTEGER,
    winners         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    finished_at     TEXT
);

CREATE TABLE IF NOT EXISTS participants (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    giveaway_id  INTEGER NOT NULL REFERENCES giveaways(id) ON DELETE CASCADE,
    user_id      INTEGER NOT NULL,
    username     TEXT,
    full_name    TEXT,
    joined_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (giveaway_id, user_id)
);

CREATE TABLE IF NOT EXISTS referrals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    giveaway_id  INTEGER NOT NULL REFERENCES giveaways(id) ON DELETE CASCADE,
    inviter_id   INTEGER NOT NULL,
    invited_id   INTEGER NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (giveaway_id, invited_id)
);

CREATE INDEX IF NOT EXISTS idx_participants_giveaway ON participants(giveaway_id);
CREATE INDEX IF NOT EXISTS idx_referrals_giveaway_inviter ON referrals(giveaway_id, inviter_id);
CREATE INDEX IF NOT EXISTS idx_giveaways_status_ends ON giveaways(status, ends_at);
