"""Idempotent script to add missing enum labels to the test database.

Usage:
    source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate lbm-arena
    python scripts/add_enum_values.py

It reads DATABASE_URL from env or falls back to known test DB.

This fixed a lot of the errors actually running tests, because the test DB
was created before we added poker as a game type and pending as a game status.
"""
import os
import sys
try:
    import psycopg2
    from psycopg2 import sql
except Exception as e:
    print("psycopg2 not available; install with: pip install psycopg2-binary")
    raise

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:XRsBD9K!_?nVMe8@db.xlcfbkzluvdnbxzwtfiq.supabase.co:5432/postgres")

print("Connecting to:", DB_URL)
conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

# Helper
def add_enum_if_missing(type_name, value):
    cur.execute(
        sql.SQL("SELECT 1 FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid WHERE t.typname = %s AND e.enumlabel = %s"),
        (type_name, value)
    )
    if cur.fetchone() is None:
        print(f"Adding {value} to {type_name}")
        cur.execute(sql.SQL("ALTER TYPE {} ADD VALUE %s").format(sql.Identifier(type_name)), (value,))
    else:
        print(f"{value} already present in {type_name}")

try:
    for v in ("chess", "poker"):
        add_enum_if_missing("gametype", v)

    for v in ("waiting", "in_progress", "completed", "aborted", "pending"):
        add_enum_if_missing("gamestatus", v)

    print("Done")
finally:
    cur.close()
    conn.close()
