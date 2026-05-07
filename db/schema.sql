-- Finder canonical DDL (Phase A + preferences) — matches Alembic 001_phase_a + 002_dating_preferences.
-- Prefer: `docker compose up -d` then `cd backend && alembic upgrade head`

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    display_name VARCHAR(120) NOT NULL,
    bio TEXT,
    birth_date DATE,
    city VARCHAR(120),
    gender VARCHAR(40),
    looking_for VARCHAR(40),
    hair_color VARCHAR(40),
    height_cm INTEGER,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_profiles_height_cm CHECK (height_cm IS NULL OR (height_cm BETWEEN 120 AND 230))
);

CREATE INDEX ix_profiles_hair_color ON profiles (hair_color);

CREATE TABLE dating_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    partner_age_min INTEGER,
    partner_age_max INTEGER,
    partner_genders TEXT[],
    partner_hair_colors TEXT[],
    prefer_same_city BOOLEAN NOT NULL DEFAULT false,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_dp_partner_age_min CHECK (partner_age_min IS NULL OR partner_age_min BETWEEN 18 AND 99),
    CONSTRAINT ck_dp_partner_age_max CHECK (partner_age_max IS NULL OR partner_age_max BETWEEN 18 AND 99),
    CONSTRAINT ck_dp_partner_age_order CHECK (
        partner_age_min IS NULL OR partner_age_max IS NULL OR partner_age_min <= partner_age_max
    )
);

CREATE INDEX ix_dating_preferences_partner_genders ON dating_preferences USING GIN (partner_genders);
CREATE INDEX ix_dating_preferences_partner_hair_colors ON dating_preferences USING GIN (partner_hair_colors);

CREATE TABLE swipes (
    id SERIAL PRIMARY KEY,
    swiper_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    target_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_swipe_not_self CHECK (swiper_user_id <> target_user_id),
    CONSTRAINT ck_swipe_direction CHECK (direction IN ('like', 'pass')),
    CONSTRAINT uq_swipe_pair UNIQUE (swiper_user_id, target_user_id)
);

CREATE INDEX ix_swipes_swiper_user_id ON swipes (swiper_user_id);
CREATE INDEX ix_swipes_target_user_id ON swipes (target_user_id);
CREATE INDEX ix_swipes_target_created ON swipes (target_user_id, created_at);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    user_low_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    user_high_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_match_order CHECK (user_low_id < user_high_id),
    CONSTRAINT uq_match_pair UNIQUE (user_low_id, user_high_id)
);

CREATE INDEX ix_matches_user_low_id ON matches (user_low_id);
CREATE INDEX ix_matches_user_high_id ON matches (user_high_id);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches (id) ON DELETE CASCADE,
    sender_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_messages_match_id ON messages (match_id);
CREATE INDEX ix_messages_sender_user_id ON messages (sender_user_id);
CREATE INDEX ix_messages_match_created ON messages (match_id, created_at);
