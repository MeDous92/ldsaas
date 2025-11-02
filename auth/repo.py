# auth/repo.py
from typing import Optional
from sqlmodel import Session, select
from models import User, Invite

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()

def create_invite(session: Session, email: str, username: str, token: str, expires_at) -> Invite:
    inv = Invite(email=email, username=username, token=token, expires_at=expires_at, status="pending")
    session.add(inv)
    session.commit()
    session.refresh(inv)
    return inv

def get_invite_by_token(session: Session, token: str) -> Optional[Invite]:
    stmt = select(Invite).where(Invite.token == token)
    return session.exec(stmt).first()

def mark_invite_accepted(session: Session, invite: Invite) -> None:
    invite.status = "accepted"
    session.add(invite)
    session.commit()

def create_user(session: Session, email: str, username: str, password_hash: str) -> User:
    user = User(email=email, username=username, password_hash=password_hash, is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
