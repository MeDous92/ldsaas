# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from db import get_session
from schemas import InviteIn, InviteOut, AcceptInviteIn, UserOut, LoginIn, LoginOut
from .service import invite_user, accept_invite
from . import repo
from .deps import get_current_user, require_admin_user
from models import User
from security import verify_password, create_access_token, create_refresh_token
from mailer import build_invite_email, send_email
import os
from urllib.parse import quote

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://app.example.com")
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    email = form.username.strip().lower()

    user = repo.get_user_by_email(session, email)
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access  = create_access_token(user_id=user.id, role=user.role)
    refresh = create_refresh_token(user_id=user.id, role=user.role)

    return LoginOut(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        user=UserOut(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
        )
    )

@router.post("/invite", response_model=InviteOut, dependencies=[Depends(require_admin_user)])
def invite(
    data: InviteIn,
    background: BackgroundTasks,
    session: Session = Depends(get_session),
    actor: User = Depends(require_admin_user),
):
    email, token = invite_user(session, data, actor_user_id=actor.id)

    # Build encoded accept-invite URL (includes optional name)
    base = f"{FRONTEND_ORIGIN}/accept-invite"
    query = f"token={quote(token)}&email={quote(email)}"
    name_part = f"&name={quote(data.name)}" if data.name else ""
    invite_url = f"{base}?{query}{name_part}"

    # Send email (now passes name + invite_url)
    msg = build_invite_email(to=email, token=token, name=data.name, invite_url=invite_url)
    background.add_task(send_email, msg)

    # Return enriched payload for the caller
    return InviteOut(email=email, token=token, name=data.name, invite_url=invite_url)

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
