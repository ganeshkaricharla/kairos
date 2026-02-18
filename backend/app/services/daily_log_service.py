from bson import ObjectId
from datetime import datetime

from app.database import get_db
from app.models.daily_log import TrackerLogInput
from app.utils.object_id import doc_id
from app.utils.dates import now


async def get_or_create_log(user_id: str, goal_id: str, date: str) -> dict:
    db = get_db()
    doc = await db.daily_logs.find_one(
        {"user_id": user_id, "goal_id": goal_id, "date": date}
    )
    if doc:
        return doc_id(doc)

    doc = {
        "user_id": user_id,
        "goal_id": goal_id,
        "date": date,
        "habit_completions": [],
        "tracker_entries": [],
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.daily_logs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc_id(doc)


async def get_daily_logs(user_id: str, date: str) -> list[dict]:
    db = get_db()
    cursor = db.daily_logs.find({"user_id": user_id, "date": date})
    return [doc_id(doc) async for doc in cursor]


async def toggle_habit(
    user_id: str, goal_id: str, date: str, habit_id: str
) -> dict:
    """Toggle habit completion. Habits can only be logged on or after their activated_at date."""
    db = get_db()

    # Check if habit is activated for this date
    habit = await db.habits.find_one({"_id": ObjectId(habit_id)})
    if not habit:
        raise ValueError("Habit not found")

    # Check if the habit is activated for this date
    if habit.get("activated_at"):
        activated_date = habit["activated_at"].date()
        log_date = datetime.strptime(date, "%Y-%m-%d").date()

        if log_date < activated_date:
            raise ValueError(
                f"This habit starts on {activated_date.isoformat()}. You can't log it before that date."
            )

    log = await db.daily_logs.find_one(
        {"user_id": user_id, "goal_id": goal_id, "date": date}
    )

    if not log:
        log_doc = {
            "user_id": user_id,
            "goal_id": goal_id,
            "date": date,
            "habit_completions": [],
            "tracker_entries": [],
            "created_at": now(),
            "updated_at": now(),
        }
        result = await db.daily_logs.insert_one(log_doc)
        log = await db.daily_logs.find_one({"_id": result.inserted_id})

    completions = log.get("habit_completions", [])
    existing = next((c for c in completions if c["habit_id"] == habit_id), None)

    if existing:
        existing["completed"] = not existing["completed"]
        existing["completed_at"] = now() if existing["completed"] else None
    else:
        completions.append(
            {
                "habit_id": habit_id,
                "completed": True,
                "completed_at": now(),
                "notes": "",
            }
        )

    await db.daily_logs.update_one(
        {"_id": log["_id"]},
        {"$set": {"habit_completions": completions, "updated_at": now()}},
    )
    updated = await db.daily_logs.find_one({"_id": log["_id"]})
    return doc_id(updated)


async def log_tracker(
    user_id: str, goal_id: str, date: str, tracker_id: str, data: TrackerLogInput
) -> dict:
    db = get_db()
    log = await db.daily_logs.find_one(
        {"user_id": user_id, "goal_id": goal_id, "date": date}
    )

    if not log:
        log_doc = {
            "user_id": user_id,
            "goal_id": goal_id,
            "date": date,
            "habit_completions": [],
            "tracker_entries": [],
            "created_at": now(),
            "updated_at": now(),
        }
        result = await db.daily_logs.insert_one(log_doc)
        log = await db.daily_logs.find_one({"_id": result.inserted_id})

    # Update tracker entry
    entries = log.get("tracker_entries", [])
    existing = next((e for e in entries if e["tracker_id"] == tracker_id), None)

    if existing:
        existing["value"] = data.value
        existing["logged_at"] = now()
        existing["notes"] = data.notes
    else:
        entries.append(
            {
                "tracker_id": tracker_id,
                "value": data.value,
                "logged_at": now(),
                "notes": data.notes,
            }
        )

    # Auto-complete linked habits
    completions = log.get("habit_completions", [])
    linked_habits = await db.habits.find(
        {"goal_id": goal_id, "linked_tracker_id": tracker_id, "status": "active"}
    ).to_list(None)

    for habit in linked_habits:
        habit_id = str(habit["_id"])
        threshold = habit.get("tracker_threshold")
        direction = await _get_tracker_direction(tracker_id)

        met = False
        if threshold is not None:
            if direction == "decrease":
                met = data.value <= threshold
            else:
                met = data.value >= threshold
        else:
            # No threshold — any log counts as completion
            met = True

        existing_completion = next(
            (c for c in completions if c["habit_id"] == habit_id), None
        )
        if existing_completion:
            existing_completion["completed"] = met
            existing_completion["completed_at"] = now() if met else None
        else:
            completions.append(
                {
                    "habit_id": habit_id,
                    "completed": met,
                    "completed_at": now() if met else None,
                    "notes": "auto-completed from tracker",
                }
            )

    await db.daily_logs.update_one(
        {"_id": log["_id"]},
        {
            "$set": {
                "tracker_entries": entries,
                "habit_completions": completions,
                "updated_at": now(),
            }
        },
    )
    updated = await db.daily_logs.find_one({"_id": log["_id"]})
    return doc_id(updated)


async def _get_tracker_direction(tracker_id: str) -> str:
    db = get_db()
    tracker = await db.trackers.find_one({"_id": ObjectId(tracker_id)})
    return tracker.get("direction", "increase") if tracker else "increase"


async def get_logs_for_period(
    user_id: str, goal_id: str, start_date: str, end_date: str
) -> list[dict]:
    db = get_db()
    cursor = db.daily_logs.find(
        {
            "user_id": user_id,
            "goal_id": goal_id,
            "date": {"$gte": start_date, "$lte": end_date},
        }
    ).sort("date", 1)
    return [doc_id(doc) async for doc in cursor]
