# Finder — database description (course submission draft)

This file is meant to match what database courses usually ask for: **domain**, **entities**, **user paths**, and enough detail that someone could **reconstruct the schema from prose alone**. Polish wording in your final PDF/report as needed.

---

## 1. Domain (field)

**Finder** is a **web dating** product: people register, maintain a **profile**, **swipe** (smash or pass) on other profiles, and when two users **mutually smash** each other the system creates a **match**. Matched users can exchange **messages**. Separately, each user can record **dating preferences** (age range, genders, hair colors, same-city bias)—these are **stated filters**, distinct from **observable traits** on profiles (e.g. gender, birth date → age, hair color, height).

---

## 2. What you need to know to reconstruct the schema

If you only had this description, you should infer roughly:

1. **users** — One row per login identity (`email` unique). Authentication material is stored as `password_hash` (implementation detail of the app).

2. **profiles** — At most **one** profile per user (`user_id` primary key → `users`). Stores presentation and **measurable traits**: display name, bio, birth date, city, **Postgres ENUM** fields for `gender`, `looking_for`, and `hair_color`, optional height in cm, plus `updated_at` for edits.

3. **dating_preferences** — At most **one** row per user (`user_id` PK/FK → `users`) for **scalar** filters: min/max partner age and `prefer_same_city`. Multi-valued filters are **not** stored as arrays (that would violate strict **1NF**); instead:
   - **dating_preference_genders** — one row per `(user_id, gender)` the user accepts;
   - **dating_preference_hair_colors** — one row per `(user_id, hair_color)` the user accepts.

4. **swipes** — Directed actions: who swiped, on whom, `direction` ENUM (`smash` / `pass`), timestamp. **No duplicate** decision for the same ordered pair `(swiper, target)`. A user cannot swipe themselves.

5. **matches** — Undirected pair of two distinct users who have **mutually smashed** each other (business rule enforced in the application when inserting). The database stores the pair as **`user_low_id` < `user_high_id`** so the same two people always map to **one** row (see §3).

6. **messages** — Belongs to a **match** via `match_id` (the chat thread). Each row has **sender**, **body**, **timestamp**. When a user opens a conversation from the match list, the app uses that match’s `id` and loads `messages` for that `match_id`. Storing both participant user ids on every message would duplicate the match entity and make “all messages in this chat” harder to index. (Optional future constraint: sender must be one of the two users in the match.)

You should also expect **foreign keys with ON DELETE CASCADE** from children to parents, **indexes** on foreign keys and common time-range / filter columns, **Postgres ENUM** types for controlled vocabularies, and **CHECK** constraints for ordering (`user_low_id < user_high_id`) and plausible numeric ranges (heights, ages).

---

## 3. Why `user_low_id` and `user_high_id`?

A match is a **relationship between two users** with no natural order. If we stored `(user_a_id, user_b_id)` without rules, the same match could appear twice as `(2, 5)` and `(5, 2)`.

**Convention:** always store the smaller `users.id` in **`user_low_id`** and the larger in **`user_high_id`**, with a **CHECK** constraint `user_low_id < user_high_id` and a **UNIQUE** constraint on `(user_low_id, user_high_id)`. The application computes `low = min(a,b)`, `high = max(a,b)` before insert.

To “find my matches” for user `U`, query:

`WHERE user_low_id = U OR user_high_id = U`.

---

## 4. Entities (tables) — short glossary

| Table | Meaning |
|-------|---------|
| users | Account. |
| profiles | Public-facing facts about the user (traits used in stats). |
| dating_preferences | Scalar partner filters (age range, same-city bias). |
| dating_preference_genders | Allowed partner genders (1NF child rows). |
| dating_preference_hair_colors | Allowed partner hair colors (1NF child rows). |
| swipes | Smash/pass events (directed). |
| matches | Mutual-smash pairs (canonical undirected storage). |
| messages | Chat inside a match (`match_id` = thread). |

---

## 5. Critical user paths (scenarios)

1. **Sign up** → insert `users` (+ `password_hash`), then `profiles`, then optional `dating_preferences` + child rows.
2. **Edit profile** → update `profiles` (and traits like `hair_color`).
3. **Set preferences** → insert/update `dating_preferences` and replace rows in `dating_preference_genders` / `dating_preference_hair_colors`.
4. **Discovery** → one batch query: not self, not already in `swipes`, optional filters (`looking_for`, `city`, `updated_at`, `dating_preferences` + child tables); then insert `swipes` per card (Phase B API).
5. **Swipe / match** → if reciprocal `smash` exists, insert `matches` with ordered pair.
6. **Chat** → user selects a match → `SELECT messages WHERE match_id = ? ORDER BY created_at`.

---

## 6. Preferences vs “who I actually matched and talked to”

- **Stated preferences** live in **`dating_preferences`** and its child tables.
- **Revealed behavior** is derived by joining:
  - `matches` (who you matched with),
  - `messages` (whether/how much you talked—e.g. message count, last message time),
  - the **partner’s** `profiles` row (their gender, `hair_color`, age from `birth_date`).

Example analysis ideas (all **SQL-friendly**):

- Average **partner age** per user among matches in the last 30 days vs `partner_age_min` / `partner_age_max`.
- Share of partners whose **`gender`** appears in `dating_preference_genders` (join or `EXISTS`).
- Share of partners whose **`hair_color`** appears in `dating_preference_hair_colors`.
- Among users with `prefer_same_city = true`, fraction of matches where `profiles.city` matches.

---

## 7. DDL sources in the repo

| Artifact | Role |
|----------|------|
| `db/schema.sql` | Single-file canonical DDL for the marker/report. |
| `db/schema.dbml` | DBML for [dbdiagram.io](https://dbdiagram.io) (export ERD image locally; not stored in Git to keep the repo small). |
| `backend/alembic/versions/` | Versioned migrations applied with Alembic. |

---

## 8. Controlled vocabularies (Postgres ENUM)

| ENUM | Values |
|------|--------|
| `profile_gender` | `woman`, `man`, `nonbinary` |
| `looking_for` | `women`, `men`, `everyone` |
| `hair_color` | `black`, `brown`, `blonde`, `red`, `gray`, `other` |
| `swipe_direction` | `smash`, `pass` |

The database rejects invalid labels at insert time; extend types with `ALTER TYPE ... ADD VALUE` when the product adds options.
