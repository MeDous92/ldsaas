# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from db import get_session
from schemas import InviteIn, InviteOut, AcceptInviteIn, UserOut
from .service import invite_user, accept_invite
from . import repo
from .deps import get_current_user, require_admin_user

from models import User
from security import verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # we use email as username
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    access = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": access, "token_type": "bearer"}

@router.post("/invite", response_model=InviteOut, dependencies=[Depends(require_admin_user)])
def invite(
    data: InviteIn,
    session: Session = Depends(get_session),
    actor: User = Depends(require_admin_user),
):
    email, token = invite_user(session, data, actor_user_id=actor.id)
    return InviteOut(email=email, token=token)

@router.post("/accept-invite")
def accept(data: AcceptInviteIn, session: Session = Depends(get_session)):
    ok = accept_invite(session, data)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")
    return {"status": "ok"}

@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return UserOut(
        id=current.id,
        email=current.email,
        name=current.name,
        role=current.role,
        is_active=current.is_active,
    )
