# app/auth/repo.py
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from models import User

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()

def create_or_update_invite(
    session: Session,
    email: str,
    name: Optional[str],
    token_hash: str,          # bcrypt-hashed token
    expires_at: datetime,
    invited_by: Optional[int] = None,
) -> User:
    user = get_user_by_email(session, email)
    if user is None:
        user = User(
            email=email,
            name=name,
            is_active=False,
            invite_token_hash=token_hash,
            invite_expires_at=expires_at,
            invited_at=datetime.utcnow(),
            invited_by=invited_by,
        )
        session.add(user)
    else:
        user.name = name or user.name
        user.is_active = False
        user.invite_token_hash = token_hash
        user.invite_expires_at = expires_at
        user.invited_at = datetime.utcnow()
        user.invited_by = invited_by

    session.commit()
    session.refresh(user)
    return user

def set_password_and_activate(session: Session, user: User, password_hash: str) -> User:
    user.password_hash = password_hash
    user.is_active = True
    user.email_verified_at = datetime.utcnow()
    user.invite_token_hash = None
    user.invite_expires_at = None
    user.invited_at = None
    user.invited_by = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
