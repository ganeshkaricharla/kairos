from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.auth.dependencies import get_current_user
from app.models.habit import HabitUpdate
from app.services import habit_service

router = APIRouter(tags=["habits"])


@router.get("/goals/{goal_id}/habits")
async def list_habits(goal_id: str, status: Optional[str] = Query(None), current_user: dict = Depends(get_current_user)):
    return await habit_service.list_habits(goal_id, status=status)


@router.patch("/habits/{habit_id}")
async def update_habit(habit_id: str, data: HabitUpdate, current_user: dict = Depends(get_current_user)):
    habit = await habit_service.update_habit(habit_id, data)
    if not habit:
        raise HTTPException(404, "Habit not found")
    return habit
