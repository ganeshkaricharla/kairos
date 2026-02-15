from bson import ObjectId

from app.database import get_db
from app.models.goal import GoalCreate, GoalUpdate
from app.utils.object_id import doc_id
from app.utils.dates import now


async def get_active_goal(user_id: str = "default") -> dict | None:
    """Return the single active goal, or None."""
    db = get_db()
    doc = await db.goals.find_one({"user_id": user_id, "status": "active"})
    return doc_id(doc) if doc else None


async def create_goal(data: GoalCreate, user_id: str) -> dict:
    db = get_db()
    existing = await get_active_goal(user_id)
    if existing:
        raise ValueError("An active goal already exists. Delete it before creating a new one.")
    doc = {
        "user_id": user_id,
        "title": data.title,
        "description": data.description,
        "target_date": data.target_date,
        "status": "active",
        "ai_context": {
            "summary": "",
            "plan_philosophy": "",
            "current_phase": "building_foundation",
            "next_review_date": None,
        },
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.goals.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_id(doc)


async def get_goal(goal_id: str) -> dict | None:
    db = get_db()
    doc = await db.goals.find_one({"_id": ObjectId(goal_id)})
    return doc_id(doc) if doc else None


async def update_goal(goal_id: str, data: GoalUpdate) -> dict | None:
    db = get_db()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        return await get_goal(goal_id)
    updates["updated_at"] = now()
    await db.goals.update_one({"_id": ObjectId(goal_id)}, {"$set": updates})
    return await get_goal(goal_id)


async def update_goal_ai_context(goal_id: str, ai_context: dict) -> dict | None:
    db = get_db()
    await db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": {"ai_context": ai_context, "updated_at": now()}},
    )
    return await get_goal(goal_id)


async def delete_goal(goal_id: str) -> bool:
    db = get_db()
    result = await db.goals.delete_one({"_id": ObjectId(goal_id)})
    if result.deleted_count:
        await db.habits.delete_many({"goal_id": goal_id})
        await db.trackers.delete_many({"goal_id": goal_id})
        await db.daily_logs.delete_many({"goal_id": goal_id})
        await db.coaching_sessions.delete_many({"goal_id": goal_id})
        return True
    return False
