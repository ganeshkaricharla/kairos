from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.daily_log import TrackerLogInput
from app.services import daily_log_service

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/{date}")
async def get_daily_logs(date: str, current_user: dict = Depends(get_current_user)):
    return await daily_log_service.get_daily_logs(current_user["id"], date)


@router.post("/{date}/goals/{goal_id}/habits/{habit_id}/toggle")
async def toggle_habit(date: str, goal_id: str, habit_id: str, current_user: dict = Depends(get_current_user)):
    return await daily_log_service.toggle_habit(current_user["id"], goal_id, date, habit_id)


@router.post("/{date}/goals/{goal_id}/trackers/{tracker_id}/log")
async def log_tracker(date: str, goal_id: str, tracker_id: str, data: TrackerLogInput, current_user: dict = Depends(get_current_user)):
    return await daily_log_service.log_tracker(
        current_user["id"], goal_id, date, tracker_id, data
    )
