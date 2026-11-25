-- =============================================================================
-- AI Business Text Assistant — схема БД (PostgreSQL)
-- 001_usage.sql
-- Применение: psql "$DATABASE_URL" -f db/001_usage.sql
--   или из контейнера: docker exec -i <postgres> psql -U <user> -d <db> < db/001_usage.sql
-- =============================================================================

-- Лог использования: одна строка на каждую сгенерированную единицу текста.
-- Используется для дневного лимита (COUNT за CURRENT_DATE) и демо-монетизации.
CREATE TABLE IF NOT EXISTS ta_usage (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT      NOT NULL,          -- Telegram user id
    chat_id     BIGINT      NOT NULL,          -- Telegram chat id
    user_name   TEXT,                          -- @username или имя
    lang        TEXT        NOT NULL DEFAULT 'ru',
    format      TEXT        NOT NULL,          -- letter | reply | post
    brief       TEXT,                          -- исходные тезисы
    result      TEXT,                          -- сгенерированный текст
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Быстрый подсчёт расхода за сегодня по конкретному пользователю.
CREATE INDEX IF NOT EXISTS idx_ta_usage_user_day
    ON ta_usage (user_id, created_at);


-- Последний запрос пользователя: нужен для кнопки «Другой вариант»/перегенерации.
-- Одна строка на пользователя (UPSERT по user_id).
CREATE TABLE IF NOT EXISTS ta_last_request (
    user_id     BIGINT      PRIMARY KEY,       -- Telegram user id
    chat_id     BIGINT      NOT NULL,
    user_name   TEXT,
    lang        TEXT        NOT NULL DEFAULT 'ru',
    brief       TEXT,                          -- последние присланные тезисы
    format      TEXT,                          -- выбранный формат (NULL пока не выбран)
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- Полезные запросы для демо/аналитики:
--
-- Расход конкретного пользователя за сегодня:
--   SELECT COUNT(*) FROM ta_usage
--   WHERE user_id = :uid AND created_at::date = CURRENT_DATE;
--
-- Топ пользователей за 7 дней:
--   SELECT user_id, user_name, COUNT(*) AS n
--   FROM ta_usage
--   WHERE created_at > NOW() - INTERVAL '7 days'
--   GROUP BY user_id, user_name ORDER BY n DESC;
--
-- Разбивка по форматам:
--   SELECT format, COUNT(*) FROM ta_usage GROUP BY format;
-- =============================================================================
