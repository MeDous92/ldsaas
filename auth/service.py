import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from schemas import InviteIn, AcceptInviteIn
from . import repo

INVITE_TTL_HOURS = 48
# Use a secret to HMAC the token before storing (safer than plain SHA256)
INVITE_SECRET = os.getenv("INVITE_SECRET", "dev-secret-change-me").encode()

def _hash_token(token: str) -> str:
    return hmac.new(INVITE_SECRET, token.encode(), hashlib.sha256).hexdigest()

def invite_user(session: Session, data: InviteIn, actor_user_id: int | None) -> tuple[str, str]:
    token = os.urandom(16).hex()
    token_hash = _hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITE_TTL_HOURS)

    user = repo.create_or_update_invite(
        session=session,
        email=data.email,
        name=data.name,
        token_hash=token_hash,
        expires_at=expires_at,
        invited_by=actor_user_id,
    )
    return (user.email, token)

def accept_invite(session: Session, data: AcceptInviteIn) -> bool:
    user = repo.get_user_by_email(session, data.email)
    if not user:
        return False
    if not user.invite_token_hash or not user.invite_expires_at:
        return False
    if datetime.now(timezone.utc) > user.invite_expires_at:
        return False

    # verify token
    given_hash = _hash_token(data.token)
    if not hmac.compare_digest(given_hash, user.invite_token_hash):
        return False

    # hash password (replace with passlib/bcrypt in production)
    password_hash = hashlib.sha256(data.password.encode()).hexdigest()
    repo.accept_invite_set_password(session, data.email, password_hash)
    return True
