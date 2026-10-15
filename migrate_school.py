"""Apply additive School MVP schema changes to the configured PostgreSQL database."""
import os
from pathlib import Path

import psycopg

url = os.environ.get("DATABASE_URL")
if not url:
    raise SystemExit("Set DATABASE_URL to the existing PostgreSQL database")

conninfo = url.replace("postgresql+psycopg://", "postgresql://", 1)
sql = Path(__file__).with_name("migration_school.sql").read_text(encoding="utf-8")
with psycopg.connect(conninfo) as connection:
    connection.execute(sql)
print("School schema migration complete; existing rows retained")
