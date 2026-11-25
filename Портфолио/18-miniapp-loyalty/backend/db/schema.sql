-- ============================================================================
--  Loyalty mini-app schema
-- ============================================================================
--  Three core tables:
--    users   — every Telegram user that opened the app (customer or admin)
--    cards   — one loyalty card per user (stamps + lifetime rewards)
--    stamps  — append-only ledger of every stamp granted (audit + stats +
--              idempotency / anti double-scan guarantee)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    tg_id       BIGINT       NOT NULL UNIQUE,      -- Telegram user id
    username    TEXT,
    first_name  TEXT,
    last_name   TEXT,
    is_admin    BOOLEAN      NOT NULL DEFAULT FALSE, -- cafe staff flag (from ADMIN_IDS)
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cards (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT      NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    code             TEXT        NOT NULL UNIQUE,        -- encoded in the customer QR
    stamps           INTEGER     NOT NULL DEFAULT 0,     -- current cycle
    rewards_earned   INTEGER     NOT NULL DEFAULT 0,     -- lifetime rewards
    rewards_redeemed INTEGER     NOT NULL DEFAULT 0,     -- lifetime redemptions
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cards_code ON cards(code);

CREATE TABLE IF NOT EXISTS stamps (
    id              BIGSERIAL PRIMARY KEY,
    card_id         BIGINT      NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    granted_by      BIGINT      NOT NULL REFERENCES users(id), -- admin user id
    -- Client-supplied unique key: guarantees a repeated/duplicated request
    -- (double scan, network retry) can never grant two stamps.
    idempotency_key TEXT        NOT NULL UNIQUE,
    completed_card  BOOLEAN     NOT NULL DEFAULT FALSE, -- did this stamp finish a card?
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_stamps_card ON stamps(card_id);
CREATE INDEX IF NOT EXISTS idx_stamps_created ON stamps(created_at);
