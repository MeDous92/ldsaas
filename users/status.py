# app/users/status.py
from datetime import datetime, timezone
from models import User

def derive_status(u: User) -> str:
    now = datetime.now(timezone.utc)
    # PENDING has top priority
    if u.password_hash is None and u.invite_expires_at and u.invite_expires_at > now:
        return "pending"
    # Then INACTIVE
    if not u.is_active:
        return "inactive"
    # Then ACTIVE
    if u.password_hash is not None and u.is_active:
        return "active"
    # Fallback
    return "inactive"
