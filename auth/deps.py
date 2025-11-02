# app/auth/deps.py
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlmodel import Session, select
from db import get_session
from models import User
from security import oauth2_scheme, JWT_SECRET, JWT_ISSUER

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience="access", issuer=JWT_ISSUER)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")
    return user

def require_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
