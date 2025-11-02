# db.py - minimal psycopg connection helpers (sync)
import os
from contextlib import contextmanager
import psycopg

DATABASE_URL = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


# One global connection pool
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg.Connection.connect(DATABASE_URL, autocommit=False)
    return _pool

@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
