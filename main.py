# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from auth.routes import router as auth_router
from routers.courses import router as courses_router
from routers.enrollments import router as enrollments_router
from routers.users import router as users_router
from routers.profiles import router as profiles_router

app = FastAPI(title="L&D SaaS Backend", version="0.1.0")

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins] if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/api/static", StaticFiles(directory="static"), name="static")

@app.get("/courses", include_in_schema=False)
def courses_page():
    return FileResponse("static/courses.html")

# mount auth
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(enrollments_router)
app.include_router(profiles_router)
