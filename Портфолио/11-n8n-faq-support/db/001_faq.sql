-- =========================================================================
-- 11-n8n-faq-support :: схема базы знаний FAQ-ассистента
-- Postgres 13+ (используется generated column + GIN индекс по tsvector)
-- =========================================================================

-- Расширение для нечёткого поиска (ILIKE-подобный триграммный fallback).
-- Если нет прав на CREATE EXTENSION — закомментируйте, поиск по tsvector
-- и ILIKE всё равно будет работать.
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- -------------------------------------------------------------------------
-- Таблица базы знаний
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS faq (
    id          BIGSERIAL PRIMARY KEY,
    question    TEXT        NOT NULL,
    answer      TEXT        NOT NULL,
    lang        TEXT        NOT NULL DEFAULT 'ru',   -- 'ru' | 'en'
    tags        TEXT[]      NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Полнотекстовый вектор: собираем из вопроса и ответа.
    -- 'simple' конфигурация не зависит от языка (работает и для RU, и для EN),
    -- поэтому подходит для смешанной базы. Вопрос имеет вес 'A' (важнее).
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', coalesce(question, '')), 'A') ||
        setweight(to_tsvector('simple', coalesce(answer,   '')), 'B')
    ) STORED
);

-- Полнотекстовый GIN-индекс
CREATE INDEX IF NOT EXISTS faq_search_vector_idx
    ON faq USING GIN (search_vector);

-- Триграммные индексы для быстрого ILIKE (нечёткий поиск по опечаткам)
CREATE INDEX IF NOT EXISTS faq_question_trgm_idx
    ON faq USING GIN (question gin_trgm_ops);
CREATE INDEX IF NOT EXISTS faq_answer_trgm_idx
    ON faq USING GIN (answer gin_trgm_ops);

-- -------------------------------------------------------------------------
-- Таблица неотвеченных вопросов (эскалация владельцу)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS unanswered (
    id          BIGSERIAL PRIMARY KEY,
    question    TEXT        NOT NULL,
    chat_id     BIGINT,                              -- Telegram chat id клиента
    username    TEXT,                                -- @username клиента
    lang        TEXT,
    status      TEXT        NOT NULL DEFAULT 'new',  -- new | resolved
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS unanswered_status_idx
    ON unanswered (status, created_at DESC);

-- -------------------------------------------------------------------------
-- Демонстрационные данные
-- -------------------------------------------------------------------------
INSERT INTO faq (question, answer, lang, tags) VALUES
  ('Какие способы оплаты вы принимаете?',
   'Мы принимаем банковские карты (Visa, Mastercard, МИР), СБП и безналичный перевод для юридических лиц.',
   'ru', ARRAY['оплата','биллинг']),
  ('Как долго идёт доставка?',
   'Доставка по городу — 1-2 рабочих дня, по стране — 3-7 рабочих дней в зависимости от региона.',
   'ru', ARRAY['доставка']),
  ('Как вернуть товар?',
   'Вернуть товар можно в течение 14 дней с момента получения. Напишите нам, и мы пришлём инструкцию по возврату.',
   'ru', ARRAY['возврат','гарантия']),
  ('What payment methods do you accept?',
   'We accept credit cards (Visa, Mastercard), bank transfer and PayPal for international customers.',
   'en', ARRAY['payment','billing']),
  ('How long does delivery take?',
   'Local delivery takes 1-2 business days; nationwide shipping takes 3-7 business days depending on the region.',
   'en', ARRAY['delivery','shipping'])
ON CONFLICT DO NOTHING;
