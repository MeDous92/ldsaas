from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from db import get_session
from schemas import InviteIn, AcceptInviteIn, UserOut, TokensOut
from .service import invite_user, accept_invite

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/invite", status_code=204)
def invite(data: InviteIn, session: Session = Depends(get_session)):
    try:
        invite_user(session, data, actor_user_id=None)  # add real actor later
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return

@router.post("/accept-invite", response_model=dict)
def accept(data: AcceptInviteIn, session: Session = Depends(get_session)):
    try:
        user, tokens = accept_invite(session, data)
        return {"user": user.dict(), "tokens": tokens.dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
