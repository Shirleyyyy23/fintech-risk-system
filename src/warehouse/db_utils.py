"""
DB connection helper (used by data-warehouse loading & later queries).
Reusable so every script connects the same way.

How to use:
  1) In PowerShell, set the password ONCE per terminal session:
       $env:DB_PASSWORD = "your_root_password"
     (Linux/macOS/Git Bash: export DB_PASSWORD="your_root_password")
  2) To test the connection right now:
       python src/warehouse/db_utils.py
     (needs MySQL running + the `fintech_risk` DB already created via sql/01_create_db.sql)
  3) Inside another script (run from project root D:\fintech-risk-system):
       import sys; from pathlib import Path
       sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
       from src.warehouse.db_utils import get_engine
       engine = get_engine()

Note: the URL is built with sqlalchemy.engine.URL.create() instead of string
concatenation, so passwords containing @ : / # ? are handled safely.
(Never build "user:pwd@host" by hand -- an '@' in the password silently
corrupts the host name and you get a confusing "getaddrinfo failed".)
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Override via env vars if needed; defaults match local setup.
DB_USER = os.environ.get("DB_USER", "root")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "fintech_risk")


def _read_password() -> str:
    pwd = os.environ.get("DB_PASSWORD")
    if not pwd:
        raise RuntimeError(
            "DB_PASSWORD not set. Run in terminal: "
            "$env:DB_PASSWORD = 'your_root_password'"
        )
    return pwd


def get_engine():
    """Return a SQLAlchemy engine. Reads password from DB_PASSWORD env var."""
    pwd = _read_password()
    url = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=pwd,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True)


def describe_target() -> None:
    """Print what we are about to connect to (password masked)."""
    pwd = os.environ.get("DB_PASSWORD") or ""
    print(f"  user     : {DB_USER}")
    print(f"  password : {'*' * len(pwd)}  (length={len(pwd)})")
    print(f"  host     : {DB_HOST}")
    print(f"  port     : {DB_PORT}")
    print(f"  database : {DB_NAME}")
    # Catch the classic "extra @ / space" typo early with a clear hint.
    if pwd != pwd.strip():
        print("  [warn] password has leading/trailing spaces")
    if pwd.startswith("@"):
        print("  [warn] password starts with '@' -- is that a typo?")


def test_connection() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        version = conn.execute(text("SELECT VERSION()")).scalar()
        dbname = conn.execute(text("SELECT DATABASE()")).scalar()
    print("MySQL connection OK")
    print(f"  server version : {version}")
    print(f"  current db     : {dbname}")
    print(f"  SELECT 1       : {result}")


if __name__ == "__main__":
    # Make project root importable so `from src...` works when run directly.
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    print("Connecting with:")
    describe_target()
    try:
        test_connection()
    except Exception as e:  # noqa: BLE001
        print()
        print("Connection failed:", e)
        print("Check: MySQL running? fintech_risk DB created? DB_PASSWORD set/correct?")
        sys.exit(1)
