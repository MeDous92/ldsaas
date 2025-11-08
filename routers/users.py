from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session, select
from models import User
from db import get_session
from auth.deps import require_admin_user, get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

def _count_active_admins(session: Session) -> int:
    stmt = select(User).where(User.role == "admin", User.is_active == True)
    return len(session.exec(stmt).all())

def _get_user_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin_user),
):
    target = _get_user_or_404(session, user_id)

    # Safety: admin must not deactivate themselves
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot deactivate themselves.")

    # Safety: don't deactivate the last active admin
    if target.role == "admin" and target.is_active:
        if _count_active_admins(session) <= 1:
            raise HTTPException(status_code=400, detail="Cannot deactivate the last active admin.")

    if not target.is_active:
        # idempotent delete semantics
        return

    target.is_active = False
    session.add(target)
    session.commit()
    return


# --- DELETE (hard): permanently erase the record ---

@router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin_user),
):
    target = _get_user_or_404(session, user_id)

    # Safety: admin must not delete themselves
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete themselves.")

    # Safety: don't delete the last active admin
    if target.role == "admin" and target.is_active:
        if _count_active_admins(session) <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last active admin.")

    # If you rely on FK constraints, this will fail fast if referential integrity is violated.
    session.delete(target)
    session.commit()
    return