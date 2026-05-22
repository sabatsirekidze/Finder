-- Finder canonical DDL (Phase A + preferences) — matches Alembic 001 + 002.
-- Prefer: `docker compose up -d` then `cd backend && alembic upgrade head`
-- After changing migrations on an existing DB: reset (see README) or downgrade to base.

CREATE TYPE swipe_direction AS ENUM ('smash', 'pass');
CREATE TYPE profile_gender AS ENUM ('woman', 'man', 'nonbinary');
CREATE TYPE looking_for AS ENUM ('women', 'men', 'everyone');
CREATE TYPE hair_color AS ENUM ('black', 'brown', 'blonde', 'red', 'gray', 'other');

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
    gender profile_gender,
    looking_for looking_for,
    hair_color hair_color,
    height_cm INTEGER,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_profiles_height_cm CHECK (height_cm IS NULL OR (height_cm BETWEEN 120 AND 230))
);

CREATE INDEX ix_profiles_hair_color ON profiles (hair_color);
CREATE INDEX ix_profiles_updated_at ON profiles (updated_at);
CREATE INDEX ix_profiles_city ON profiles (city);

CREATE TABLE dating_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    partner_age_min INTEGER,
    partner_age_max INTEGER,
    prefer_same_city BOOLEAN NOT NULL DEFAULT false,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_dp_partner_age_min CHECK (partner_age_min IS NULL OR partner_age_min BETWEEN 18 AND 99),
    CONSTRAINT ck_dp_partner_age_max CHECK (partner_age_max IS NULL OR partner_age_max BETWEEN 18 AND 99),
    CONSTRAINT ck_dp_partner_age_order CHECK (
        partner_age_min IS NULL OR partner_age_max IS NULL OR partner_age_min <= partner_age_max
    )
);

-- 1NF: one row per allowed gender / hair color (no TEXT[] repeating groups).
CREATE TABLE dating_preference_genders (
    user_id INTEGER NOT NULL REFERENCES dating_preferences (user_id) ON DELETE CASCADE,
    gender profile_gender NOT NULL,
    PRIMARY KEY (user_id, gender)
);

CREATE INDEX ix_dating_preference_genders_gender ON dating_preference_genders (gender);

CREATE TABLE dating_preference_hair_colors (
    user_id INTEGER NOT NULL REFERENCES dating_preferences (user_id) ON DELETE CASCADE,
    hair_color hair_color NOT NULL,
    PRIMARY KEY (user_id, hair_color)
);

CREATE INDEX ix_dating_preference_hair_colors_hair_color ON dating_preference_hair_colors (hair_color);

CREATE TABLE swipes (
    id SERIAL PRIMARY KEY,
    swiper_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    target_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    direction swipe_direction NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_swipe_not_self CHECK (swiper_user_id <> target_user_id),
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

-- match_id = conversation thread (user opens a match, then loads messages for that match_id).
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
