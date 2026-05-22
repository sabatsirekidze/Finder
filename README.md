# Finder

Custom Tinder-like dating app (course project). **Phase A** adds the database foundation only — see [`docs/PHASES.md`](docs/PHASES.md) for how later phases are split.

**Course-oriented database write-up** (domain, entities, user paths, `user_low`/`user_high`, preferences vs behavior): [`docs/DATABASE_COURSE_DESCRIPTION.md`](docs/DATABASE_COURSE_DESCRIPTION.md).

## Phase A — run locally

**Prerequisites:** Docker Desktop, Python 3.11+.

1. Copy environment file:

   ```bash
   copy .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d
   ```

3. Create a venv and install backend tooling (kept minimal on purpose):

   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Apply migrations (from `backend/` with venv active):

   ```bash
   alembic upgrade head
   ```

5. Seed fake data:

   ```bash
   python ..\db\seeds\seed.py
   ```

6. **ERD image for the report:** paste `db/schema.dbml` into [dbdiagram.io](https://dbdiagram.io) and export — see [`docs/images/README.md`](docs/images/README.md).

### Test Phase A (smoke check)

With Docker Desktop **running** and steps 1–5 done (or at least DB up + `alembic upgrade head`):

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\verify_phase_a.py
```

Or from the scripts folder:

```powershell
cd backend\scripts
..\.venv\Scripts\activate
python verify_phase_a.py
```

You should see `OK: connected`, all tables listed (including `dating_preference_genders` and `dating_preference_hair_colors`), Alembic revision `002_dating_preferences`, and non-zero row counts after seeding.

**Schema changed on an existing DB?** Reset volumes (see **Reset database** below) or run `alembic upgrade head` for new revisions (e.g. `003_discovery_indexes`).

**Optional manual SQL** (password `finder` from `.env.example`):

```powershell
docker exec -it finder-postgres-1 psql -U finder -d finder -c "SELECT COUNT(*) FROM users;"
```

If your container name differs, run `docker ps` and substitute the `postgres` service container name.

**No Docker?** Install PostgreSQL locally, set `DATABASE_URL` in `.env` to your instance, then run `alembic upgrade head`, `python ..\db\seeds\seed.py`, and `python scripts\verify_phase_a.py` again.

### Layout

| Path | Purpose |
|------|---------|
| `docker-compose.yml` | Local Postgres 16 |
| `backend/app/models.py` | SQLAlchemy models (source of truth with migrations) |
| `backend/alembic/` | Schema revisions |
| `db/schema.sql` | Canonical DDL copy for submissions |
| `db/schema.dbml` | DBML for dbdiagram |
| `db/seeds/seed.py` | Faker seed |

### Reset database

Use this after pulling schema changes on Phase A (e.g. ENUM types, 1NF preference tables):

```bash
docker compose down -v
docker compose up -d
cd backend
alembic upgrade head
python ..\db\seeds\seed.py
```
