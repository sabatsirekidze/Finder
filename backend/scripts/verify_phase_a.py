"""
Smoke-test Phase A: DB reachable, Alembic applied, tables exist, optional row counts.

Usage (from repo root or backend):

  cd backend
  ..\\.venv\\Scripts\\activate   # if not already
  python scripts\\verify_phase_a.py

Requires DATABASE_URL in ..\\.env (see ..\\.env.example).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(REPO_ROOT / ".env")

TABLES_EXPECTED = (
    "users",
    "profiles",
    "dating_preferences",
    "dating_preference_genders",
    "dating_preference_hair_colors",
    "swipes",
    "matches",
    "messages",
    "alembic_version",
)


def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set. Copy .env.example to .env at repo root.")
        return 1

    try:
        engine = create_engine(url, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("OK: connected to Postgres.")
    except OSError as e:
        print(f"ERROR: cannot connect — is Docker running and postgres up?\n  {e}")
        return 1
    except Exception as e:
        print(f"ERROR: connection failed:\n  {e}")
        return 1

    insp = inspect(engine)
    existing = set(insp.get_table_names())
    missing = [t for t in TABLES_EXPECTED if t not in existing]
    if missing:
        print(f"ERROR: missing tables: {missing}")
        print("Run: cd backend && alembic upgrade head")
        return 1
    print(f"OK: all expected tables present ({len(TABLES_EXPECTED)}).")

    with engine.connect() as conn:
        rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
        if rev:
            print(f"OK: Alembic revision at head: {rev}")
        else:
            print("WARN: alembic_version empty — run alembic upgrade head")

    counts: list[tuple[str, int]] = []
    with engine.connect() as conn:
        for t in (
            "users",
            "profiles",
            "dating_preferences",
            "swipes",
            "matches",
            "messages",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one()
            counts.append((t, int(n)))

    print("Row counts:")
    for t, n in counts:
        print(f"  {t}: {n}")

    if counts[0][1] == 0:
        print("HINT: database is empty — run: python ..\\db\\seeds\\seed.py (from backend/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
