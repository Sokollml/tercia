-- 001_orders.sql
-- Схема БД для мини-аппа поиска фриланс-заказов.
-- Применяется к тому же Postgres, где живёт n8n (или к отдельной БД freelance_orders).
-- Идемпотентно: можно прогонять повторно.

-- =========================================================
-- raw_messages: сырые сообщения из чатов (пишет collector, ТОЛЬКО INSERT)
-- =========================================================
CREATE TABLE IF NOT EXISTS raw_messages (
    id          BIGSERIAL PRIMARY KEY,
    chat        TEXT        NOT NULL,          -- @username или id чата-источника
    author      TEXT,                          -- username автора сообщения (может быть NULL)
    text        TEXT        NOT NULL,
    text_hash   TEXT        NOT NULL UNIQUE,    -- sha256 нормализованного текста -> дедуп
    status      TEXT        NOT NULL DEFAULT 'pending',  -- pending | processing | done | skipped
    message_link TEXT,                          -- t.me/<chat>/<message_id> если удалось построить
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_raw_messages_status ON raw_messages (status);
CREATE INDEX IF NOT EXISTS idx_raw_messages_created_at ON raw_messages (created_at DESC);

-- =========================================================
-- orders: результат ИИ-классификации (пишет n8n classify workflow)
-- =========================================================
CREATE TABLE IF NOT EXISTS orders (
    id              BIGSERIAL PRIMARY KEY,
    raw_message_id  BIGINT REFERENCES raw_messages (id) ON DELETE SET NULL,
    source_chat     TEXT        NOT NULL,
    author_username TEXT,
    raw_text        TEXT        NOT NULL,
    service_type    TEXT,                          -- design | dev | copywriting | smm | ...
    summary         TEXT,                          -- краткий бриф своими словами
    budget          NUMERIC,                       -- число или NULL
    urgency         TEXT        NOT NULL DEFAULT 'low',  -- low | medium | high
    languages       JSONB       NOT NULL DEFAULT '[]'::jsonb,  -- ["ru","en"]
    skills_required JSONB       NOT NULL DEFAULT '[]'::jsonb,  -- ["figma","react"]
    message_link    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_service_type ON orders (service_type);
CREATE INDEX IF NOT EXISTS idx_orders_urgency ON orders (urgency);
-- GIN-индексы для фильтрации по массивам навыков/языков
CREATE INDEX IF NOT EXISTS idx_orders_skills ON orders USING GIN (skills_required);
CREATE INDEX IF NOT EXISTS idx_orders_languages ON orders USING GIN (languages);

-- =========================================================
-- users: настройки пользователя мини-аппа (per-user)
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    tg_id       BIGINT PRIMARY KEY,             -- Telegram user id из initData
    settings    JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Пример settings:
-- {
--   "skills": ["figma","react"],
--   "keywords": ["лендинг","бот"],
--   "min_budget": 5000,
--   "languages": ["ru","en"],
--   "service_types": ["design","dev"]
-- }

-- =========================================================
-- user_order_status: связь пользователь <-> заказ (статус + заметка)
-- =========================================================
CREATE TABLE IF NOT EXISTS user_order_status (
    user_tg_id  BIGINT NOT NULL REFERENCES users (tg_id) ON DELETE CASCADE,
    order_id    BIGINT NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    status      TEXT   NOT NULL DEFAULT 'new',   -- new | interested | hidden | responded
    note        TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_tg_id, order_id)
);

CREATE INDEX IF NOT EXISTS idx_uos_user ON user_order_status (user_tg_id);
CREATE INDEX IF NOT EXISTS idx_uos_status ON user_order_status (status);
