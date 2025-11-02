from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from schemas import InviteIn, InviteOut, AcceptInviteIn, UserOut
from .service import invite_user, accept_invite
from . import repo

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/invite", response_model=InviteOut)
def invite(data: InviteIn, session: Session = Depends(get_session)):
    email, token = invite_user(session, data, actor_user_id=None)
    return InviteOut(email=email, token=token)

@router.post("/accept-invite")
def accept(data: AcceptInviteIn, session: Session = Depends(get_session)):
    ok = accept_invite(session, data)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")
    return {"status": "ok"}

@router.get("/me", response_model=UserOut)
def me(session: Session = Depends(get_session)):
    # stub until JWT is added: just return first active user
    user = repo.get_user_by_email(session, "admin@example.com") or repo.get_user_by_email(session, "you@example.com")
    if not user:
        raise HTTPException(404, "No user")
    return UserOut(id=user.id, email=user.email, name=user.name, role=user.role, is_active=user.is_active)
