-- SQLite schema (local development / tests).
-- Timestamps are stored as UNIX epoch seconds (INTEGER, UTC).
-- Boolean-ish flags use INTEGER 0/1 to stay uniform with the Postgres schema.

-- Per-chat settings. One row per group the bot is a member of.
CREATE TABLE IF NOT EXISTS chats (
    chat_id           INTEGER PRIMARY KEY,          -- telegram chat id (negative)
    title             TEXT    NOT NULL DEFAULT '',
    lang              TEXT    NOT NULL DEFAULT 'ru',

    -- Editable texts.
    rules_text        TEXT    NOT NULL DEFAULT '',
    welcome_text      TEXT    NOT NULL DEFAULT '',

    -- Captcha module.
    captcha_enabled   INTEGER NOT NULL DEFAULT 1,
    captcha_timeout   INTEGER NOT NULL DEFAULT 60,  -- seconds before kick

    -- Antispam module.
    filter_links      INTEGER NOT NULL DEFAULT 1,   -- block links from newcomers
    filter_forwards   INTEGER NOT NULL DEFAULT 0,   -- block forwarded messages
    filter_stopwords  INTEGER NOT NULL DEFAULT 1,   -- block messages with stop-words
    stopwords         TEXT    NOT NULL DEFAULT '',  -- comma-separated list

    -- Antiflood module.
    antiflood_enabled INTEGER NOT NULL DEFAULT 1,
    antiflood_limit   INTEGER NOT NULL DEFAULT 5,   -- messages ...
    antiflood_window  INTEGER NOT NULL DEFAULT 5,   -- ... per this many seconds

    -- Warnings escalation.
    warn_limit        INTEGER NOT NULL DEFAULT 3,   -- active warns -> auto mute
    mute_duration     INTEGER NOT NULL DEFAULT 3600,-- seconds of auto mute

    created_at        INTEGER NOT NULL
);

-- Every warning ever issued. "active" lets us count / reset without deleting
-- the audit trail.
CREATE TABLE IF NOT EXISTS warnings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,             -- warned user
    admin_id    INTEGER NOT NULL,             -- who issued (0 = bot/auto)
    reason      TEXT    NOT NULL DEFAULT '',
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  INTEGER NOT NULL
);

-- Active / historical mutes. until_ts = 0 means permanent (until manual unmute).
CREATE TABLE IF NOT EXISTS mutes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    admin_id    INTEGER NOT NULL DEFAULT 0,   -- 0 = auto (warn threshold / flood)
    reason      TEXT    NOT NULL DEFAULT '',
    until_ts    INTEGER NOT NULL DEFAULT 0,   -- epoch seconds; 0 = permanent
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  INTEGER NOT NULL
);

-- Newcomers awaiting captcha. Survives restarts so pending checks are not lost.
CREATE TABLE IF NOT EXISTS captcha_pending (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    message_id  INTEGER NOT NULL DEFAULT 0,   -- challenge message to delete later
    answer      TEXT    NOT NULL,             -- expected button token
    deadline_ts INTEGER NOT NULL,             -- kick if unsolved by then
    created_at  INTEGER NOT NULL,
    UNIQUE (chat_id, user_id)
);

-- Full audit log of moderation actions.
CREATE TABLE IF NOT EXISTS action_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL,
    actor_id    INTEGER NOT NULL DEFAULT 0,   -- admin id, or 0 for the bot
    target_id   INTEGER NOT NULL DEFAULT 0,
    action      TEXT    NOT NULL,             -- warn|mute|unmute|ban|kick|captcha_pass|captcha_fail|spam_delete
    details     TEXT    NOT NULL DEFAULT '',
    created_at  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_warn_chat_user ON warnings(chat_id, user_id, active);
CREATE INDEX IF NOT EXISTS idx_mute_chat_user ON mutes(chat_id, user_id, active);
CREATE INDEX IF NOT EXISTS idx_pending_deadline ON captcha_pending(deadline_ts);
CREATE INDEX IF NOT EXISTS idx_log_chat ON action_log(chat_id, created_at);
