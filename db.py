# db.py
import os
from typing import Generator
from sqlmodel import create_engine, Session

# One place to read the URL
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql+psycopg://user:pass@host:5432/dbname

# Create a single engine (no self-imports!)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# FastAPI dependency
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
