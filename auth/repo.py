from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlmodel import Session

def row_to_user_out(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row.get("name"),
        "role": row["role"],
        "created_at": row["created_at"],
    }

def get_user_by_email(session: Session, email: str) -> Optional[Dict[str, Any]]:
    q = text("""
        SELECT id, email, name, role, password_hash, is_active,
               invited_at, invited_by, invite_token_hash, invite_expires_at,
               email_verified_at, created_at
        FROM users
        WHERE email = :email
        LIMIT 1
    """)
    row = session.exec(q, {"email": email}).mappings().first()
    return dict(row) if row else None

def create_user_invited(session: Session, *, email: str, name: str|None, role: str,
                        invited_by: int|None, invite_token_hash: str, invite_expires_at) -> Dict[str, Any]:
    q = text("""
        INSERT INTO users (email, name, role, is_active, invited_at, invited_by, invite_token_hash, invite_expires_at)
        VALUES (:email, :name, :role, false, now(), :invited_by, :invite_token_hash, :invite_expires_at)
        RETURNING id, email, name, role, created_at
    """)
    row = session.exec(q, {"email": email, "name": name, "role": role,
                           "invited_by": invited_by, "invite_token_hash": invite_token_hash,
                           "invite_expires_at": invite_expires_at}).mappings().one()
    return dict(row)

def update_user_invite(session: Session, *, user_id: int, invite_token_hash: str, invite_expires_at, invited_by: int|None) -> Dict[str, Any]:
    q = text("""
        UPDATE users
        SET invited_at = now(),
            invited_by = :invited_by,
            invite_token_hash = :invite_token_hash,
            invite_expires_at = :invite_expires_at
        WHERE id = :user_id
        RETURNING id, email, name, role, created_at
    """)
    row = session.exec(q, {"user_id": user_id, "invited_by": invited_by,
                           "invite_token_hash": invite_token_hash, "invite_expires_at": invite_expires_at}).mappings().one()
    return dict(row)

def accept_invite_set_password(session: Session, *, email: str, password_hash: str) -> Dict[str, Any]:
    q = text("""
        UPDATE users
        SET password_hash = :password_hash,
            invite_token_hash = NULL,
            invite_expires_at = NULL,
            email_verified_at = now(),
            is_active = true,
            updated_at = now()
        WHERE email = :email
        RETURNING id, email, name, role, created_at
    """)
    row = session.exec(q, {"email": email, "password_hash": password_hash}).mappings().one()
    return dict(row)
