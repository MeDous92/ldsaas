# auth/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select

from db import get_session
from models import User
from security import JWT_SECRET, JWT_ISSUER

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def _decode_access_token(token: str) -> dict:
    try:
        # HS256 verification; also enforce issuer and audience
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": True}, audience="access")
        if payload.get("iss") != JWT_ISSUER:
            raise JWTError("Bad issuer")
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e

def get_current_user(session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    payload = _decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Malformed token")
    user = session.exec(select(User).where(User.id == int(sub))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not active or not found")
    return user

def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user
