# Finder

Custom Tinder-like dating app (course project). See [`docs/PHASES.md`](docs/PHASES.md) for the phase breakdown.

**Course-oriented database write-up:** [`docs/DATABASE_COURSE_DESCRIPTION.md`](docs/DATABASE_COURSE_DESCRIPTION.md).

## Quick start

**Prerequisites:** Docker Desktop, Python 3.11+.

### 1. Environment

```bash
cp .env.example .env   # Mac/Linux
copy .env.example .env # Windows
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Install backend dependencies

```bash
cd backend
python -m venv .venv

# Mac/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Apply migrations

```bash
# from backend/ with venv active
alembic upgrade head
```

### 5. Seed fake data

```bash
# Mac/Linux
python ../db/seeds/seed.py
# Windows
python ..\db\seeds\seed.py
```

### 6. Start the backend server

```bash
# from backend/ with venv active
uvicorn app.main:app --reload
```

API is now running at **http://localhost:8000**.  
Interactive docs (Swagger UI): **http://localhost:8000/docs**

---

## Viewing the database

Use **TablePlus** (recommended, free tier sufficient) or DBeaver:

| Field    | Value       |
|----------|-------------|
| Host     | `localhost` |
| Port     | `5432`      |
| User     | `finder`    |
| Password | `finder`    |
| Database | `finder`    |

---

## Smoke check (Phase A)

```bash
# from backend/ with venv active
python scripts/verify_phase_a.py
```

---

## Layout

| Path | Purpose |
|------|---------|
| `docker-compose.yml` | Local Postgres 16 |
| `backend/app/main.py` | FastAPI entry point |
| `backend/app/models.py` | SQLAlchemy models |
| `backend/app/routers/` | Route handlers (auth, profiles, discovery, swipes, matches, messages, stats) |
| `backend/alembic/` | Schema migrations |
| `db/schema.dbml` | DBML for [dbdiagram.io](https://dbdiagram.io) |
| `db/seeds/seed.py` | Faker seed script |

---

## Reset database

Use after pulling schema changes or to start fresh:

```bash
docker compose down -v
docker compose up -d
cd backend
alembic upgrade head
python ../db/seeds/seed.py  # Mac/Linux
```
