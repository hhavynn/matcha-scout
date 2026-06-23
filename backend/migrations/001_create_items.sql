-- Matcha Scout PostgreSQL compatibility schema.
--
-- The first migration preserves the existing DynamoDB item contract in JSONB.
-- This minimizes application risk while moving hosting away from AWS. A later
-- migration can normalize cafes, drinks, reviews, and profiles independently.

CREATE TABLE IF NOT EXISTS matcha_items (
    pk TEXT NOT NULL,
    sk TEXT NOT NULL,
    gsi1pk TEXT,
    gsi1sk TEXT,
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (pk, sk)
);

CREATE INDEX IF NOT EXISTS matcha_items_gsi1_idx
    ON matcha_items (gsi1pk, gsi1sk)
    WHERE gsi1pk IS NOT NULL;

CREATE INDEX IF NOT EXISTS matcha_items_sk_idx
    ON matcha_items (sk);
