import os, logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel import SQLModel, select, Session
from models import Employee
from db import engine, get_session

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="L&D SaaS API (dev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Skip auto-create in prod (prevents crash if DB not reachable)
    if os.getenv("ENV", "dev") != "prod":
        try:
            SQLModel.metadata.create_all(engine)
        except Exception as e:
            log.error(f"DB init failed (dev mode): {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/employees", response_model=List[Employee])
def list_employees(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)):
    return session.exec(select(Employee).limit(limit).offset(offset)).all()

@app.get("/hello")
def hello():
    return "Hello"