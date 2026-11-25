-- 001_monitor.sql
-- Схема БД для проекта «мониторинг источника + отчёт по расписанию».
-- СУБД: PostgreSQL (тот же Postgres, что использует n8n на VPS, либо отдельная БД).
--
-- Модель данных:
--   monitor_items      — текущее «живое» состояние записей источника (актуальный снапшот).
--                        Апсертится каждый прогон; пропавшие записи гасятся is_active = false.
--   monitor_snapshots  — журнал зафиксированных изменений (audit log) для истории/отчётов.

-- ─────────────────────────────────────────────────────────────
-- Текущее состояние записей источника
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monitor_items (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key   TEXT        NOT NULL,               -- какой источник (см. Source Config в workflow)
    external_id  TEXT        NOT NULL,               -- стабильный id записи у источника (дедуп)
    title        TEXT,
    company      TEXT,
    price        NUMERIC(14, 2),                     -- зарплата/цена; NULL если не указана
    url          TEXT,
    fingerprint  TEXT,                               -- хэш значимых полей для детекта «обновилось»
    is_active    BOOLEAN     NOT NULL DEFAULT TRUE,  -- FALSE = запись пропала из источника
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Дедуп: одна запись источника = одна строка.
    CONSTRAINT uq_monitor_items UNIQUE (source_key, external_id)
);

-- Индексы под типовые запросы workflow.
CREATE INDEX IF NOT EXISTS idx_monitor_items_active
    ON monitor_items (source_key, is_active);
CREATE INDEX IF NOT EXISTS idx_monitor_items_last_seen
    ON monitor_items (last_seen_at);

-- ─────────────────────────────────────────────────────────────
-- Журнал изменений (история отчётов)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monitor_snapshots (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key   TEXT        NOT NULL,
    run_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    change_type  TEXT        NOT NULL,               -- 'added' | 'updated' | 'price_drop' | 'removed'
    external_id  TEXT        NOT NULL,
    title        TEXT,
    company      TEXT,
    price        NUMERIC(14, 2),
    prev_price   NUMERIC(14, 2),                     -- заполняется для price_drop
    payload      JSONB                               -- полный снимок item на момент изменения
);

CREATE INDEX IF NOT EXISTS idx_monitor_snapshots_source_run
    ON monitor_snapshots (source_key, run_at DESC);
CREATE INDEX IF NOT EXISTS idx_monitor_snapshots_change_type
    ON monitor_snapshots (change_type);
