-- Canonical SQLite schema for the community quiz bot (local development).
-- The application creates these tables automatically via SQLAlchemy
-- (Base.metadata.create_all); this file mirrors that schema for reference.

CREATE TABLE IF NOT EXISTS seasons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       VARCHAR(255) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT 0,
    started_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at    DATETIME
);

CREATE TABLE IF NOT EXISTS questions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    category      VARCHAR(100) NOT NULL,
    lang          VARCHAR(2)   NOT NULL DEFAULT 'ru',
    text          TEXT NOT NULL,
    options       JSON NOT NULL,           -- array of option strings
    correct_index INTEGER NOT NULL,
    explanation   TEXT,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_questions_category ON questions (category);
CREATE INDEX IF NOT EXISTS ix_questions_lang ON questions (lang);

CREATE TABLE IF NOT EXISTS quizzes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id       VARCHAR(128) NOT NULL UNIQUE,
    chat_id       BIGINT NOT NULL,
    message_id    BIGINT,
    question_id   INTEGER REFERENCES questions(id) ON DELETE SET NULL,
    season_id     INTEGER REFERENCES seasons(id) ON DELETE SET NULL,
    mode          VARCHAR(16) NOT NULL DEFAULT 'daily',
    correct_index INTEGER NOT NULL,
    opened_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closes_at     DATETIME,
    is_closed     BOOLEAN NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_quizzes_poll_id ON quizzes (poll_id);

CREATE TABLE IF NOT EXISTS answers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id      INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    poll_id      VARCHAR(128) NOT NULL,
    user_id      BIGINT NOT NULL,
    username     VARCHAR(255),
    option_index INTEGER NOT NULL,
    is_correct   BOOLEAN NOT NULL DEFAULT 0,
    points       INTEGER NOT NULL DEFAULT 0,
    answered_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_answer_poll_user UNIQUE (poll_id, user_id)  -- double-answer guard
);
CREATE INDEX IF NOT EXISTS ix_answers_poll_id ON answers (poll_id);
CREATE INDEX IF NOT EXISTS ix_answers_user_id ON answers (user_id);

CREATE TABLE IF NOT EXISTS scores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id     INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    user_id       BIGINT NOT NULL,
    username      VARCHAR(255),
    points        INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    total_count   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT uq_score_season_user UNIQUE (season_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_scores_season_id ON scores (season_id);
CREATE INDEX IF NOT EXISTS ix_scores_user_id ON scores (user_id);

CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id       BIGINT PRIMARY KEY,
    lang          VARCHAR(2) NOT NULL DEFAULT 'ru',
    daily_enabled BOOLEAN NOT NULL DEFAULT 0
);
