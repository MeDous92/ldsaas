# service.py
import os
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from schemas import InviteIn, AcceptInviteIn
from . import repo
from security import hash_password, hash_token, verify_token  # <- bcrypt-based

INVITE_TTL_HOURS = 48

def invite_user(session: Session, data: InviteIn, actor_user_id: int | None) -> tuple[str, str]:
    # Generate a random plaintext token for the invite link/email
    token = os.urandom(16).hex()
    # Store only a bcrypt hash of that token in DB
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITE_TTL_HOURS)

    user = repo.create_or_update_invite(
        session=session,
        email=data.email,
        name=data.name,
        token_hash=token_hash,
        expires_at=expires_at,
        invited_by=actor_user_id,
    )
    # Return plaintext token to caller (to send via email/DM)
    return (user.email, token)

def accept_invite(session: Session, data: AcceptInviteIn) -> bool:
    user = repo.get_user_by_email(session, data.email)
    if not user or not user.invite_token_hash or not user.invite_expires_at:
        return False
    if datetime.now(timezone.utc) > user.invite_expires_at:
        return False

    # Verify plaintext token against bcrypt hash
    if not verify_token(data.token, user.invite_token_hash):
        return False

    # Hash password with bcrypt and activate user
    repo.accept_invite_set_password(session, data.email, hash_password(data.password))
    return True
