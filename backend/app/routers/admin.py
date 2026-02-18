from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_admin
from app.config import settings
from app.database import get_db
from app.utils.object_id import doc_id

router = APIRouter(prefix="/admin", tags=["admin"])


class SystemSettings(BaseModel):
    """System-wide configuration settings"""
    session_lock_enabled: bool
    session_lock_hours: int


class UpdateSettingsRequest(BaseModel):
    session_lock_enabled: bool | None = None
    session_lock_hours: int | None = None


@router.get("/settings")
async def get_settings(current_admin: dict = Depends(get_current_admin)):
    """Get current system settings (admin only)"""
    return {
        "session_lock_enabled": settings.session_lock_enabled,
        "session_lock_hours": settings.session_lock_hours,
        "admin_emails": settings.admin_emails,
    }


@router.patch("/settings")
async def update_settings(
    data: UpdateSettingsRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Update system settings (admin only)

    Note: This updates the in-memory settings for the current session.
    For permanent changes, update the .env file.
    """
    if data.session_lock_enabled is not None:
        settings.session_lock_enabled = data.session_lock_enabled

    if data.session_lock_hours is not None:
        if data.session_lock_hours < 1 or data.session_lock_hours > 168:
            raise HTTPException(400, "Lock hours must be between 1 and 168 (1 week)")
        settings.session_lock_hours = data.session_lock_hours

    return {
        "session_lock_enabled": settings.session_lock_enabled,
        "session_lock_hours": settings.session_lock_hours,
        "message": "Settings updated (in-memory only - update .env for persistence)"
    }


@router.get("/users")
async def list_users(
    current_admin: dict = Depends(get_current_admin),
    limit: int = 50,
    skip: int = 0
):
    """Get list of all users (admin only)"""
    db = get_db()

    # Get total count
    total = await db.users.count_documents({})

    # Get paginated users
    cursor = db.users.find({}).skip(skip).limit(limit).sort("created_at", -1)
    users = [doc_id(user) async for user in cursor]

    # Remove sensitive data
    for user in users:
        user.pop("ai_api_key_encrypted", None)

    return {
        "users": users,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


@router.get("/stats")
async def get_stats(current_admin: dict = Depends(get_current_admin)):
    """Get system statistics (admin only)"""
    db = get_db()

    total_users = await db.users.count_documents({})
    total_goals = await db.goals.count_documents({})
    total_habits = await db.habits.count_documents({})
    total_sessions = await db.coaching_sessions.count_documents({})
    active_sessions = await db.coaching_sessions.count_documents({"status": "active"})

    return {
        "total_users": total_users,
        "total_goals": total_goals,
        "total_habits": total_habits,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
    }
