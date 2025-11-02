import os
from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from jose import jwt

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ISSUER = os.environ.get("JWT_ISSUER", "ldsaas")
ACCESS_TTL_MIN = int(os.environ.get("ACCESS_TTL_MIN", "30"))
REFRESH_TTL_DAYS = int(os.environ.get("REFRESH_TTL_DAYS", "7"))

def hash_password(plain: str) -> str:
    return bcrypt.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)

def hash_token(raw: str) -> str:
    # store invites like passwords
    return bcrypt.hash(raw)

def verify_token(raw: str, hashed: str) -> bool:
    return bcrypt.verify(raw, hashed)

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
