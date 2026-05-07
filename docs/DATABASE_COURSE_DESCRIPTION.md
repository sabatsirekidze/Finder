# Finder — database description (course submission draft)

This file is meant to match what database courses usually ask for: **domain**, **entities**, **user paths**, and enough detail that someone could **reconstruct the schema from prose alone**. Polish wording in your final PDF/report as needed.

---

## 1. Domain (field)

**Finder** is a **web dating** product: people register, maintain a **profile**, **swipe** (like or pass) on other profiles, and when two users **mutually like** each other the system creates a **match**. Matched users can exchange **messages**. Separately, each user can record **dating preferences** (age range, genders, hair colors, same-city bias)—these are **stated filters**, distinct from **observable traits** on profiles (e.g. gender, birth date → age, hair color, height).

---

## 2. What you need to know to reconstruct the schema

If you only had this description, you should infer roughly:

1. **users** — One row per login identity (`email` unique). Authentication material is stored as `password_hash` (implementation detail of the app).

2. **profiles** — At most **one** profile per user (`user_id` primary key → `users`). Stores presentation and **measurable traits**: display name, bio, birth date, city, gender, hair color, optional height in cm, plus `looking_for` as a simple label. `updated_at` tracks edits.

3. **dating_preferences** — At most **one** row per user (`user_id` PK/FK → `users`). Stores **stated partner filters**: min/max partner age, allowed partner genders and hair colors as **Postgres arrays** (easy to query with `&&`, `ANY`, `unnest`), and a boolean `prefer_same_city`. This is **not** auto-derived from behavior; the app collects it from the user (or seed data). **Analytics** compare this table to **actual** partners found via matches.

4. **swipes** — Directed actions: who swiped, on whom, `like` or `pass`, timestamp. **No duplicate** decision for the same ordered pair `(swiper, target)`. A user cannot swipe themselves.

5. **matches** — Undirected pair of two distinct users who have **mutually liked** each other (business rule enforced in the application when inserting). The database stores the pair as **`user_low_id` < `user_high_id`** so the same two people always map to **one** row (see §3).

6. **messages** — Belongs to a **match**; has **sender**, **body**, **timestamp**. (Optional future constraint: sender must be one of the two users in the match—can be added in a later migration.)

You should also expect **foreign keys with ON DELETE CASCADE** from children to parents, **indexes** on foreign keys and common time-range / filter columns (including **GIN** on preference arrays for overlap queries), and **CHECK** constraints for enums (`direction`), ordering (`user_low_id < user_high_id`), and plausible numeric ranges (heights, ages).

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
| profiles | Public-facing facts about the user (including traits used in stats). |
| dating_preferences | User-supplied partner filters (arrays + age range + same-city bias). |
| swipes | Like/pass events (directed). |
| matches | Mutual-like pairs (canonical undirected storage). |
| messages | Chat inside a match. |

---

## 5. Critical user paths (scenarios)

1. **Sign up** → insert `users` (+ `password_hash`), then `profiles`, then optional `dating_preferences`.
2. **Edit profile** → update `profiles` (and traits like `hair_color`).
3. **Set preferences** → insert/update `dating_preferences`.
4. **Swipe** → insert `swipes`; if reciprocal `like` exists, insert `matches` with ordered pair.
5. **Chat** → insert `messages` under an existing `match`.

---

## 6. Preferences vs “who I actually matched and talked to”

- **Stated preferences** live in **`dating_preferences`**.
- **Revealed behavior** is derived by joining:
  - `matches` (who you matched with),
  - `messages` (whether/how much you talked—e.g. message count, last message time),
  - the **partner’s** `profiles` row (their gender, `hair_color`, age from `birth_date`).

Example analysis ideas (all **SQL-friendly**):

- Average **partner age** per user among matches in the last 30 days vs `partner_age_min` / `partner_age_max`.
- Share of partners whose **`gender`** appears in `partner_genders` (array overlap).
- Share of partners whose **`hair_color`** appears in `partner_hair_colors`.
- Among users with `prefer_same_city = true`, fraction of matches where `profiles.city` matches.

Array columns use **GIN** indexes so overlap filters stay cheap at moderate scale.

---

## 7. DDL sources in the repo

| Artifact | Role |
|----------|------|
| `db/schema.sql` | Single-file canonical DDL for the marker/report. |
| `db/schema.dbml` | DBML for [dbdiagram.io](https://dbdiagram.io) (export ERD image locally; not stored in Git to keep the repo small). |
| `backend/alembic/versions/` | Versioned migrations applied with Alembic. |

---

## 8. Controlled vocabularies (recommended)

Keep values consistent so aggregates are meaningful:

- **gender / partner_genders:** e.g. `woman`, `man`, `nonbinary` (extend as needed).
- **hair_color / partner_hair_colors:** e.g. `black`, `brown`, `blonde`, `red`, `gray`, `other`.

The schema allows free text; the app or seed data should **standardize** strings.
