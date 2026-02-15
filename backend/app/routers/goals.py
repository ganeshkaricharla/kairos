from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.models.goal import GoalCreate, GoalUpdate
from app.services import goal_service, habit_service, tracker_service, coaching_service

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("")
async def create_goal(data: GoalCreate, current_user: dict = Depends(get_current_user)):
    try:
        goal = await goal_service.create_goal(data, user_id=current_user["id"])
    except ValueError as e:
        raise HTTPException(409, str(e))

    # Auto-start a coaching session for conversational goal setup
    await coaching_service.start_coaching_session(
        goal["id"], trigger="goal_setup", user_id=current_user["id"]
    )

    return goal


@router.get("")
async def get_active_goal(current_user: dict = Depends(get_current_user)):
    """Return the single active goal (with habits + trackers), or null."""
    goal = await goal_service.get_active_goal(user_id=current_user["id"])
    if not goal:
        return None
    goal["habits"] = await habit_service.list_habits(goal["id"], status="active")
    goal["trackers"] = await tracker_service.list_trackers(goal["id"])
    return goal


@router.get("/{goal_id}")
async def get_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    goal = await goal_service.get_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    goal["habits"] = await habit_service.list_habits(goal_id, status="active")
    goal["trackers"] = await tracker_service.list_trackers(goal_id)
    return goal


@router.patch("/{goal_id}")
async def update_goal(goal_id: str, data: GoalUpdate, current_user: dict = Depends(get_current_user)):
    goal = await goal_service.update_goal(goal_id, data)
    if not goal:
        raise HTTPException(404, "Goal not found")
    return goal


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    deleted = await goal_service.delete_goal(goal_id)
    if not deleted:
        raise HTTPException(404, "Goal not found")
    return {"deleted": True}
