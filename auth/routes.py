# auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from schemas import InviteIn, InviteOut, AcceptInviteIn, UserOut
from .service import invite_user, accept_invite
from . import repo
from .deps import require_admin_user, get_current_user
from security import verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/invite", response_model=InviteOut)
def invite(
    data: InviteIn,
    session: Session = Depends(get_session),
    admin = Depends(require_admin_user),   # <--- admin gate
):
    email, token = invite_user(session, data, actor_user_id=admin.id)
    return InviteOut(email=email, token=token)

@router.post("/accept-invite")
def accept(data: AcceptInviteIn, session: Session = Depends(get_session)):
    ok = accept_invite(session, data)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")
    return {"status": "ok"}

# Minimal username/password login for admins & regular users
# (Assumes the user already has a password_hash — e.g., your seeded admin)
from pydantic import BaseModel
class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginIn, session: Session = Depends(get_session)):
    user = repo.get_user_by_email(session, data.email)
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return {
        "access_token": create_access_token(user.id, user.role),
        "token_type": "bearer",
        "role": user.role,
    }

@router.get("/me", response_model=UserOut)
def me(current = Depends(get_current_user)):
    return UserOut(
        id=current.id,
        email=current.email,
        name=current.name,
        role=current.role,
        is_active=current.is_active,
    )
