# app/security.py
import os
from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


JWT_SECRET = os.getenv("JWT_SECRET") or "_dev_only_change_me_"
JWT_ISSUER = os.getenv("JWT_ISSUER", "ldsaas")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "30"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "7"))

def hash_password(plain: str) -> str:
    return bcrypt.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)

def _jwt(sub: int, role: str, ttl: timedelta, aud: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "role": role,
        "iss": JWT_ISSUER,
        "aud": aud,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def create_access_token(user_id: int, role: str) -> str:
    return _jwt(user_id, role, timedelta(minutes=ACCESS_TTL_MIN), "access")

def create_refresh_token(user_id: int, role: str) -> str:
    return _jwt(user_id, role, timedelta(days=REFRESH_TTL_DAYS), "refresh")

# Used by FastAPI dependencies to extract the bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
