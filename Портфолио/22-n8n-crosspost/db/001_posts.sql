-- 001_posts.sql
-- Схема очереди кросс-постинга для n8n (Postgres).
-- Применение:  psql -U <user> -d <db> -f db/001_posts.sql
--         или: docker exec -i <postgres_container> psql -U <user> -d <db> < db/001_posts.sql

-- Статусы поста в очереди:
--   queued     — запланирован / ждёт публикации
--   publishing — взят в работу планировщиком (защита от двойной отправки)
--   published  — успешно опубликован во все целевые каналы
--   error      — публикация упала (см. last_error), возможен retry
CREATE TABLE IF NOT EXISTS posts (
    id            BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    text          TEXT        NOT NULL DEFAULT '',
    media_url     TEXT,                          -- ссылка на медиа (фото/видео) или NULL
    media_type    TEXT,                          -- 'photo' | 'video' | 'document' | NULL
    channels      JSONB       NOT NULL DEFAULT '[]'::jsonb,   -- массив целевых платформ/каналов, напр. ["telegram","vk"]
    publish_at    TIMESTAMPTZ NOT NULL DEFAULT now(),          -- время публикации (сейчас = мгновенно)
    status        TEXT        NOT NULL DEFAULT 'queued',
    retry_count   INTEGER     NOT NULL DEFAULT 0,
    last_error    TEXT,                          -- текст последней ошибки для диагностики
    result        JSONB,                         -- ответ платформы (message_id и т.п.) для логирования
    source        TEXT,                          -- откуда пришёл пост: 'telegram_bot' | 'webhook_form'
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at  TIMESTAMPTZ
);

-- Индексы под запросы планировщика (выборка «пора публиковать»).
CREATE INDEX IF NOT EXISTS idx_posts_due
    ON posts (publish_at)
    WHERE status = 'queued';

CREATE INDEX IF NOT EXISTS idx_posts_status      ON posts (status);
CREATE INDEX IF NOT EXISTS idx_posts_publish_at  ON posts (publish_at);
CREATE INDEX IF NOT EXISTS idx_posts_created_at  ON posts (created_at DESC);

-- Автообновление updated_at при любом UPDATE.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_posts_updated_at ON posts;
CREATE TRIGGER trg_posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Опционально: таблица журнала попыток публикации (детальное логирование).
CREATE TABLE IF NOT EXISTS post_logs (
    id          BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id     BIGINT      NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    channel     TEXT        NOT NULL,            -- 'telegram' | 'vk' | ...
    status      TEXT        NOT NULL,            -- 'published' | 'error'
    detail      JSONB,                           -- ответ платформы или текст ошибки
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_post_logs_post_id ON post_logs (post_id);
