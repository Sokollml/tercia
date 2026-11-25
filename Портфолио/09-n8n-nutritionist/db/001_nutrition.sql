-- 001_nutrition.sql
-- Схема БД для ассистента-нутрициолога (n8n + Postgres).
-- Идемпотентный накат: можно запускать повторно.

-- ============================================================
-- Таблица пользователей Telegram
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    tg_user_id  BIGINT      NOT NULL UNIQUE,   -- id пользователя в Telegram
    username    TEXT,                          -- @username (может отсутствовать)
    first_name  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Таблица записей о приёмах пищи
-- ============================================================
CREATE TABLE IF NOT EXISTS entries (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dish        TEXT        NOT NULL,          -- распознанное блюдо
    kcal        INTEGER     NOT NULL DEFAULT 0,
    protein_g   NUMERIC(7,2) NOT NULL DEFAULT 0,
    fat_g       NUMERIC(7,2) NOT NULL DEFAULT 0,
    carbs_g     NUMERIC(7,2) NOT NULL DEFAULT 0,
    confidence  NUMERIC(4,3) NOT NULL DEFAULT 0,  -- уверенность LLM 0..1
    note        TEXT,                          -- комментарий модели
    raw_text    TEXT,                          -- исходное сообщение пользователя
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_kcal_nonneg    CHECK (kcal >= 0),
    CONSTRAINT chk_protein_nonneg CHECK (protein_g >= 0),
    CONSTRAINT chk_fat_nonneg     CHECK (fat_g >= 0),
    CONSTRAINT chk_carbs_nonneg   CHECK (carbs_g >= 0)
);

-- ============================================================
-- Индексы
-- ============================================================
-- Для команд /today и /week — выборки по пользователю и дате.
CREATE INDEX IF NOT EXISTS idx_entries_user_created
    ON entries (user_id, created_at DESC);

-- Быстрый подсчёт дневного лимита (user_id + дата).
CREATE INDEX IF NOT EXISTS idx_entries_user_day
    ON entries (user_id, (created_at::date));

-- Поиск пользователя по Telegram id.
CREATE INDEX IF NOT EXISTS idx_users_tg_user_id
    ON users (tg_user_id);

-- ============================================================
-- (Опционально) Проверка дневного лимита на уровне БД.
-- Лимит для демо также контролируется в SQL воркфлоу (WHERE cnt.c < $limit)
-- и в Code-ноде. Ниже — пример-справка, как посчитать записи за сегодня:
--
--   SELECT count(*) FROM entries e
--   JOIN users u ON u.id = e.user_id
--   WHERE u.tg_user_id = :tg_id AND e.created_at::date = CURRENT_DATE;
-- ============================================================
