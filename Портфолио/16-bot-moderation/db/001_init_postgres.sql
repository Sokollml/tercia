-- PostgreSQL schema (production).
-- Timestamps are stored as UNIX epoch seconds (BIGINT, UTC).
-- Flags use SMALLINT 0/1 so the application SQL is identical across drivers.

CREATE TABLE IF NOT EXISTS chats (
    chat_id           BIGINT   PRIMARY KEY,          -- telegram chat id (negative)
    title             TEXT     NOT NULL DEFAULT '',
    lang              TEXT     NOT NULL DEFAULT 'ru',

    rules_text        TEXT     NOT NULL DEFAULT '',
    welcome_text      TEXT     NOT NULL DEFAULT '',

    captcha_enabled   SMALLINT NOT NULL DEFAULT 1,
    captcha_timeout   INTEGER  NOT NULL DEFAULT 60,

    filter_links      SMALLINT NOT NULL DEFAULT 1,
    filter_forwards   SMALLINT NOT NULL DEFAULT 0,
    filter_stopwords  SMALLINT NOT NULL DEFAULT 1,
    stopwords         TEXT     NOT NULL DEFAULT '',

    antiflood_enabled SMALLINT NOT NULL DEFAULT 1,
    antiflood_limit   INTEGER  NOT NULL DEFAULT 5,
    antiflood_window  INTEGER  NOT NULL DEFAULT 5,

    warn_limit        INTEGER  NOT NULL DEFAULT 3,
    mute_duration     INTEGER  NOT NULL DEFAULT 3600,

    created_at        BIGINT   NOT NULL
);

CREATE TABLE IF NOT EXISTS warnings (
    id          BIGSERIAL PRIMARY KEY,
    chat_id     BIGINT   NOT NULL,
    user_id     BIGINT   NOT NULL,
    admin_id    BIGINT   NOT NULL,
    reason      TEXT     NOT NULL DEFAULT '',
    active      SMALLINT NOT NULL DEFAULT 1,
    created_at  BIGINT   NOT NULL
);

CREATE TABLE IF NOT EXISTS mutes (
    id          BIGSERIAL PRIMARY KEY,
    chat_id     BIGINT   NOT NULL,
    user_id     BIGINT   NOT NULL,
    admin_id    BIGINT   NOT NULL DEFAULT 0,
    reason      TEXT     NOT NULL DEFAULT '',
    until_ts    BIGINT   NOT NULL DEFAULT 0,
    active      SMALLINT NOT NULL DEFAULT 1,
    created_at  BIGINT   NOT NULL
);

CREATE TABLE IF NOT EXISTS captcha_pending (
    id          BIGSERIAL PRIMARY KEY,
    chat_id     BIGINT   NOT NULL,
    user_id     BIGINT   NOT NULL,
    message_id  BIGINT   NOT NULL DEFAULT 0,
    answer      TEXT     NOT NULL,
    deadline_ts BIGINT   NOT NULL,
    created_at  BIGINT   NOT NULL,
    UNIQUE (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS action_log (
    id          BIGSERIAL PRIMARY KEY,
    chat_id     BIGINT   NOT NULL,
    actor_id    BIGINT   NOT NULL DEFAULT 0,
    target_id   BIGINT   NOT NULL DEFAULT 0,
    action      TEXT     NOT NULL,
    details     TEXT     NOT NULL DEFAULT '',
    created_at  BIGINT   NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_warn_chat_user ON warnings(chat_id, user_id, active);
CREATE INDEX IF NOT EXISTS idx_mute_chat_user ON mutes(chat_id, user_id, active);
CREATE INDEX IF NOT EXISTS idx_pending_deadline ON captcha_pending(deadline_ts);
CREATE INDEX IF NOT EXISTS idx_log_chat ON action_log(chat_id, created_at);
