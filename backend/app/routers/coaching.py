from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.services import coaching_service

router = APIRouter(tags=["coaching"])


class MessageInput(BaseModel):
    message: str


@router.get("/goals/{goal_id}/coaching")
async def get_active_coaching(goal_id: str, current_user: dict = Depends(get_current_user)):
    session = await coaching_service.get_active_session(goal_id)
    return session


@router.post("/goals/{goal_id}/coaching/start")
async def start_coaching(goal_id: str, trigger: str = "scheduled_review", current_user: dict = Depends(get_current_user)):
    return await coaching_service.start_coaching_session(goal_id, trigger, user_id=current_user["id"])


@router.post("/coaching/{session_id}/message")
async def send_message(session_id: str, data: MessageInput, current_user: dict = Depends(get_current_user)):
    try:
        return await coaching_service.send_message(session_id, data.message)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/coaching/{session_id}/accept-change/{index}")
async def accept_change(session_id: str, index: int, current_user: dict = Depends(get_current_user)):
    try:
        return await coaching_service.accept_change(session_id, index)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/coaching/{session_id}/reject-change/{index}")
async def reject_change(session_id: str, index: int, current_user: dict = Depends(get_current_user)):
    try:
        return await coaching_service.reject_change(session_id, index)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/coaching/{session_id}/resolve")
async def resolve_session(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return await coaching_service.resolve_session(session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
