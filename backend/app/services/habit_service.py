from bson import ObjectId

from app.database import get_db
from app.models.habit import HabitCreate, HabitUpdate
from app.utils.object_id import doc_id
from app.utils.dates import now


async def create_habit(data: HabitCreate, user_id: str) -> dict:
    db = get_db()
    doc = {
        "goal_id": data.goal_id,
        "user_id": user_id,
        "title": data.title,
        "description": data.description,
        "frequency": data.frequency,
        "time_of_day": data.time_of_day,
        "duration_minutes": data.duration_minutes,
        "difficulty": data.difficulty,
        "reasoning": data.reasoning,
        "status": data.status,
        "activated_at": now() if data.status == "active" else None,
        "replaced_by": None,
        "replaces": None,
        "order": data.order,
        "linked_tracker_id": data.linked_tracker_id,
        "tracker_threshold": data.tracker_threshold,
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.habits.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_id(doc)


async def list_habits(goal_id: str, status: str | None = None) -> list[dict]:
    db = get_db()
    query = {"goal_id": goal_id}
    if status:
        query["status"] = status
    cursor = db.habits.find(query).sort("order", 1)
    return [doc_id(doc) async for doc in cursor]


async def get_habit(habit_id: str) -> dict | None:
    db = get_db()
    doc = await db.habits.find_one({"_id": ObjectId(habit_id)})
    return doc_id(doc) if doc else None


async def update_habit(habit_id: str, data: HabitUpdate) -> dict | None:
    db = get_db()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        return await get_habit(habit_id)
    updates["updated_at"] = now()
    if "status" in updates and updates["status"] == "active":
        updates["activated_at"] = now()
    await db.habits.update_one({"_id": ObjectId(habit_id)}, {"$set": updates})
    return await get_habit(habit_id)
