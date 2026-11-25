-- ─────────────────────────────────────────────────────────────────────────────
--  Схема БД трекера привычек. Диалект — PostgreSQL (целевая БД).
--  Для локальных тестов миграция автоматически транслируется в SQLite
--  (см. backend/src/migrate.ts, функция toSqlite).
-- ─────────────────────────────────────────────────────────────────────────────

-- Пользователи. id — это Telegram user id (приходит в initData.user.id).
CREATE TABLE IF NOT EXISTS users (
  id            BIGINT PRIMARY KEY,
  username      TEXT,
  first_name    TEXT,
  last_name     TEXT,
  language_code TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Привычки, привязанные к пользователю.
CREATE TABLE IF NOT EXISTS habits (
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  emoji      TEXT NOT NULL DEFAULT '✅',
  color      TEXT NOT NULL DEFAULT '#6C5CE7',
  archived   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_habits_user ON habits(user_id);

-- Отметки выполнения. day хранится строкой 'YYYY-MM-DD' (локальный день пользователя):
-- это избавляет от расхождений часовых поясов и одинаково работает в PG и SQLite.
CREATE TABLE IF NOT EXISTS checkins (
  id         BIGSERIAL PRIMARY KEY,
  habit_id   BIGINT NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
  day        TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (habit_id, day)
);

CREATE INDEX IF NOT EXISTS idx_checkins_habit ON checkins(habit_id);
