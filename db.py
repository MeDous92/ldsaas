# db.py
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# load .env from the same directory as main.py (current working dir)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Create a .env file with DATABASE_URL=...")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session
