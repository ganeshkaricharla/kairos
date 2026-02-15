from bson import ObjectId

from app.database import get_db
from app.models.tracker import TrackerCreate, TrackerUpdate
from app.utils.object_id import doc_id
from app.utils.dates import now


async def create_tracker(data: TrackerCreate, user_id: str) -> dict:
    db = get_db()
    doc = {
        "goal_id": data.goal_id,
        "user_id": user_id,
        "name": data.name,
        "description": data.description,
        "unit": data.unit,
        "type": data.type,
        "direction": data.direction,
        "target_value": data.target_value,
        "current_value": data.current_value,
        "reasoning": data.reasoning,
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.trackers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_id(doc)


async def list_trackers(goal_id: str) -> list[dict]:
    db = get_db()
    cursor = db.trackers.find({"goal_id": goal_id})
    return [doc_id(doc) async for doc in cursor]


async def get_tracker(tracker_id: str) -> dict | None:
    db = get_db()
    doc = await db.trackers.find_one({"_id": ObjectId(tracker_id)})
    return doc_id(doc) if doc else None


async def update_tracker(tracker_id: str, data: TrackerUpdate) -> dict | None:
    db = get_db()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        return await get_tracker(tracker_id)
    updates["updated_at"] = now()
    await db.trackers.update_one({"_id": ObjectId(tracker_id)}, {"$set": updates})
    return await get_tracker(tracker_id)
