import os
from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from jose import jwt

# <-- make env reads safe at import time
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    # dev fallback so the container won’t crash; set a real secret in Coolify envs
    JWT_SECRET = "_dev_only_change_me_"
    print("WARNING: JWT_SECRET not set; using insecure dev secret.")

JWT_ISSUER = os.getenv("JWT_ISSUER", "ldsaas")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "30"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "7"))

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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def _decode(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience="access", issuer=JWT_ISSUER)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    payload = _decode(token)
    user_id = int(payload["sub"])
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or not found")
    return user

def require_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user