# Phases and branches

Work is split so each phase stays reviewable and the repo stays small (no generated frontend bundles in Git).

| Phase | Branch (suggested) | What lands in the repo |
|-------|--------------------|-------------------------|
| **A** | `PhaseA` | Postgres via Docker, SQLAlchemy models, Alembic migrations, `dating_preferences` + profile traits (supports discovery filters: city, gender, looking_for, age/hair prefs), discovery indexes, `db/schema.sql`, `db/schema.dbml`, Faker seed, [`DATABASE_COURSE_DESCRIPTION.md`](DATABASE_COURSE_DESCRIPTION.md). **No** batch recommendation API yet — Phase B. |
| **B** | `PhaseB` | FastAPI app, CRUD, match creation rules, optional SQL files for the three report queries. |
| **C** | `PhaseC` | React (Vite) client; env points at local API. |
| **D** | `PhaseD` or `main` | Report assets only if needed (ERD PNG export is **not** stored — generate from `db/schema.dbml`). |
| **E** | `PhaseE` | Deployment configs only (e.g. `render.yaml`, env templates) — keep secrets out of Git. |

**Workflow:** merge `PhaseA` → `main` when stable; open `PhaseB` from `main`, and so on. Alternatively keep one long-lived branch per phase and merge at the end — avoid committing `node_modules/`, `.venv/`, or Docker layer caches.

See root `README.md` for how to run Phase A.
