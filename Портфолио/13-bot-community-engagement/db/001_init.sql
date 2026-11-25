-- Community Engagement bot — initial schema (PostgreSQL).
-- Applied automatically by the app on first run via SQLAlchemy metadata,
-- but kept here as an explicit, reviewable migration for production.

CREATE TABLE IF NOT EXISTS chats (
    id                    BIGINT PRIMARY KEY,
    title                 VARCHAR(255),
    lang                  VARCHAR(8)  NOT NULL DEFAULT 'ru',

    welcome_enabled       BOOLEAN     NOT NULL DEFAULT TRUE,
    xp_enabled            BOOLEAN     NOT NULL DEFAULT TRUE,
    leaderboard_enabled   BOOLEAN     NOT NULL DEFAULT TRUE,
    daily_prompt_enabled  BOOLEAN     NOT NULL DEFAULT TRUE,

    welcome_text_ru       TEXT,
    welcome_text_en       TEXT,

    xp_per_message        INTEGER     NOT NULL DEFAULT 5,
    xp_cooldown_sec       INTEGER     NOT NULL DEFAULT 60,
    min_message_len       INTEGER     NOT NULL DEFAULT 3,
    antiflood_window_sec  INTEGER     NOT NULL DEFAULT 5,

    daily_prompt_time     VARCHAR(5)  NOT NULL DEFAULT '10:00',
    weekly_top_dow        INTEGER     NOT NULL DEFAULT 0,
    weekly_top_time       VARCHAR(5)  NOT NULL DEFAULT '12:00',

    created_at            TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS members (
    chat_id           BIGINT      NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_id           BIGINT      NOT NULL,
    username          VARCHAR(255),
    full_name         VARCHAR(255),

    xp                INTEGER     NOT NULL DEFAULT 0,
    level             INTEGER     NOT NULL DEFAULT 0,
    streak            INTEGER     NOT NULL DEFAULT 0,

    last_active_date  DATE,
    last_xp_at        TIMESTAMP,
    created_at        TIMESTAMP   NOT NULL DEFAULT NOW(),

    PRIMARY KEY (chat_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_members_chat_xp ON members (chat_id, xp DESC);

CREATE TABLE IF NOT EXISTS daily_prompts (
    id          SERIAL PRIMARY KEY,
    chat_id     BIGINT,               -- NULL = global pool
    kind        VARCHAR(16) NOT NULL DEFAULT 'question',  -- question | poll
    text_ru     TEXT        NOT NULL,
    text_en     TEXT        NOT NULL,
    options_ru  TEXT,                 -- pipe-separated "a|b|c"
    options_en  TEXT,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    chat_id     BIGINT      NOT NULL,
    user_id     BIGINT      NOT NULL,
    type        VARCHAR(32) NOT NULL DEFAULT 'xp',   -- xp | levelup | streak | join
    xp          INTEGER     NOT NULL DEFAULT 0,
    meta        TEXT,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_chat_created ON events (chat_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_chat_user    ON events (chat_id, user_id);
