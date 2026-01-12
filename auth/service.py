# app/auth/service.py
import os
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from schemas import InviteIn, AcceptInviteIn
from . import repo
from security import hash_password, oauth2_scheme
from passlib.hash import bcrypt
from users.status import derive_status

INVITE_TTL_HOURS = int(os.getenv("INVITE_TTL_HOURS", "48"))

def _hash_invite_token(raw: str) -> str:
    # Store a bcrypt hash of the token (like a password)
    return bcrypt.hash(raw)

def _verify_invite_token(raw: str, hashed: str) -> bool:
    return bcrypt.verify(raw, hashed)

def invite_user(session: Session, data: InviteIn, actor_user_id: int | None, role: str) -> tuple[str, str]:
    raw_token = os.urandom(16).hex()
    token_hash = _hash_invite_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITE_TTL_HOURS)

    user = repo.create_or_update_invite(
        session=session,
        email=data.email,
        name=data.name,
        token_hash=token_hash,
        expires_at=expires_at,
        invited_by=actor_user_id,
        role=role,
    )
        # Keep invited users INACTIVE until they accept
    user.is_active = False
    user.status = derive_status(user)  # -> "pending"
    session.add(user)
    session.commit()
    # Return the token (shown once); email or UI sends it to the invitee
    return (user.email, raw_token)

def accept_invite(session: Session, data: AcceptInviteIn) -> bool:
    user = repo.get_user_by_email(session, data.email)
    if not user:
        return False
    if not user.invite_token_hash or not user.invite_expires_at:
        return False
    if datetime.now(timezone.utc) > user.invite_expires_at:
        return False

    if not _verify_invite_token(data.token, user.invite_token_hash):
        return False

    user.password_hash = hash_password(data.password)
    user.invite_token_hash = None
    user.invite_expires_at = None
    user.email_verified_at = datetime.now(timezone.utc)

    # Activate on acceptance
    user.is_active = True
    user.status = derive_status(user)  # -> "active"
    session.add(user)
    session.commit()
    return True
