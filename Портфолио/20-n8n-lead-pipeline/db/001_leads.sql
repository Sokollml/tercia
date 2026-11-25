-- ============================================================
-- 20-n8n-lead-pipeline · схема БД
-- Накат: psql "$DATABASE_URL" -f db/001_leads.sql
-- Идемпотентно: можно запускать повторно (IF NOT EXISTS).
-- ============================================================

BEGIN;

-- --- Таблица заявок --------------------------------------------------
CREATE TABLE IF NOT EXISTS leads (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hash         TEXT        NOT NULL,        -- хеш заявки для идемпотентности
    type         TEXT        NOT NULL DEFAULT 'manual_review'
                 CHECK (type IN ('lead', 'question', 'spam', 'manual_review')),
    name         TEXT        NOT NULL DEFAULT '',
    contact      TEXT        NOT NULL DEFAULT '',
    summary      TEXT        NOT NULL DEFAULT '',
    budget       TEXT        NOT NULL DEFAULT '',
    source       TEXT        NOT NULL DEFAULT 'website',
    raw_message  TEXT        NOT NULL DEFAULT '',
    is_spam      BOOLEAN     NOT NULL DEFAULT FALSE,
    fallback     BOOLEAN     NOT NULL DEFAULT FALSE,  -- сработал ли fallback ИИ
    received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Идемпотентность: один и тот же хеш заявки не создаёт дубль.
-- Используется в INSERT ... ON CONFLICT (hash) DO NOTHING.
CREATE UNIQUE INDEX IF NOT EXISTS uq_leads_hash ON leads (hash);

-- Индексы под типовые выборки (дневная сводка, фильтры по типу).
CREATE INDEX IF NOT EXISTS idx_leads_received_at ON leads (received_at);
CREATE INDEX IF NOT EXISTS idx_leads_type        ON leads (type);
CREATE INDEX IF NOT EXISTS idx_leads_is_spam     ON leads (is_spam);

-- --- Таблица уведомлений (журнал отправленных сообщений) -------------
CREATE TABLE IF NOT EXISTS notifications (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lead_id    BIGINT      REFERENCES leads (id) ON DELETE SET NULL,
    channel    TEXT        NOT NULL DEFAULT 'telegram',
    status     TEXT        NOT NULL DEFAULT 'sent'
               CHECK (status IN ('sent', 'failed', 'skipped')),
    payload    JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_lead_id    ON notifications (lead_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications (created_at);

COMMIT;
