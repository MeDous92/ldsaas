import os, secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple
from sqlmodel import Session
from schemas import InviteIn, AcceptInviteIn, UserOut, TokensOut
from security import hash_token, verify_token, hash_password, create_access_token, create_refresh_token
from . import repo

FRONT_URL = os.environ.get("APP_FRONTEND_URL", "http://localhost:5173")

def invite_user(session: Session, data: InviteIn, actor_user_id: int | None = None) -> None:
    user = repo.get_user_by_email(session, data.email)
    raw = secrets.token_urlsafe(32)
    token_hash = hash_token(raw)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    if user:
        if user["is_active"]:
            raise ValueError("User already active")
        repo.update_user_invite(session, user_id=user["id"], invite_token_hash=token_hash,
                                invite_expires_at=expires, invited_by=actor_user_id)
        link_user = {"email": user["email"]}
    else:
        new_u = repo.create_user_invited(session, email=data.email, name=data.name or None,
                                         role=data.role or "employee", invited_by=actor_user_id,
                                         invite_token_hash=token_hash, invite_expires_at=expires)
        link_user = {"email": new_u["email"]}

    link = f"{FRONT_URL}/accept-invite?token={raw}&email={link_user['email']}"
    print("INVITE LINK:", link)  # TODO: replace with email send
    # no return

def accept_invite(session: Session, data: AcceptInviteIn) -> Tuple[UserOut, TokensOut]:
    user = repo.get_user_by_email(session, data.email)
    if not user:
        raise ValueError("No such invite")

    if not user.get("invite_expires_at"):
        raise ValueError("Invite not found")

    if user["invite_expires_at"] < datetime.now(timezone.utc):
        raise ValueError("Invite expired")

    if not verify_token(data.token, user["invite_token_hash"]):
        raise ValueError("Invalid token")

    pw_hash = hash_password(data.password)
    updated = repo.accept_invite_set_password(session, email=data.email, password_hash=pw_hash)

    access = create_access_token(updated["id"], updated["role"])
    refresh = create_refresh_token(updated["id"], updated["role"])
    return UserOut(**updated), TokensOut(access_token=access, refresh_token=refresh)
