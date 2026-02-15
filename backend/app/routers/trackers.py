from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.models.tracker import TrackerUpdate
from app.services import tracker_service

router = APIRouter(tags=["trackers"])


@router.get("/goals/{goal_id}/trackers")
async def list_trackers(goal_id: str, current_user: dict = Depends(get_current_user)):
    return await tracker_service.list_trackers(goal_id)


@router.patch("/trackers/{tracker_id}")
async def update_tracker(tracker_id: str, data: TrackerUpdate, current_user: dict = Depends(get_current_user)):
    tracker = await tracker_service.update_tracker(tracker_id, data)
    if not tracker:
        raise HTTPException(404, "Tracker not found")
    return tracker
