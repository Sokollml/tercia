-- PostgreSQL schema for the giveaway bot.
-- Applied automatically on startup (see bot/db.py).

CREATE TABLE IF NOT EXISTS giveaways (
    id              BIGSERIAL PRIMARY KEY,
    chat_id         BIGINT      NOT NULL,          -- chat where it was announced
    creator_id      BIGINT      NOT NULL,          -- admin who created it
    prize           TEXT        NOT NULL,
    description     TEXT,
    winners_count   INTEGER     NOT NULL DEFAULT 1,
    points_per_ref  INTEGER     NOT NULL DEFAULT 1, -- extra tickets per referral
    required_channel TEXT,                          -- @channel to be subscribed, or NULL
    seed            TEXT        NOT NULL,           -- fixed at creation, used for the draw
    status          TEXT        NOT NULL DEFAULT 'active', -- active | finished | cancelled
    ends_at         TIMESTAMPTZ NOT NULL,
    announce_msg_id BIGINT,                         -- message with the "Участвую" button
    winners         TEXT,                           -- JSON array of winner user_ids (after draw)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS participants (
    id           BIGSERIAL PRIMARY KEY,
    giveaway_id  BIGINT      NOT NULL REFERENCES giveaways(id) ON DELETE CASCADE,
    user_id      BIGINT      NOT NULL,
    username     TEXT,
    full_name    TEXT,
    joined_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- One account = one entry per giveaway (anti-cheat).
    UNIQUE (giveaway_id, user_id)
);

CREATE TABLE IF NOT EXISTS referrals (
    id           BIGSERIAL PRIMARY KEY,
    giveaway_id  BIGINT      NOT NULL REFERENCES giveaways(id) ON DELETE CASCADE,
    inviter_id   BIGINT      NOT NULL,             -- who shared the link
    invited_id   BIGINT      NOT NULL,             -- who joined via the link
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- An invited user can only ever be credited once per giveaway.
    UNIQUE (giveaway_id, invited_id)
);

CREATE INDEX IF NOT EXISTS idx_participants_giveaway ON participants(giveaway_id);
CREATE INDEX IF NOT EXISTS idx_referrals_giveaway_inviter ON referrals(giveaway_id, inviter_id);
CREATE INDEX IF NOT EXISTS idx_giveaways_status_ends ON giveaways(status, ends_at);
