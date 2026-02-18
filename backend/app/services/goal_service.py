from bson import ObjectId

from app.database import get_db
from app.models.goal import GoalCreate, GoalUpdate
from app.models.goal_template import get_template_by_id
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

    # Get goal template
    template = get_template_by_id(data.template_id)
    if not template:
        raise ValueError(f"Invalid template_id: {data.template_id}")

    # Determine direction based on initial vs target values
    if data.initial_value is not None and data.target_value is not None:
        direction = "decrease" if data.target_value < data.initial_value else "increase"
    else:
        direction = "increase"  # Default if values not provided

    # Create goal with template data
    doc = {
        "user_id": user_id,
        "template_id": template.id,
        "title": template.name,
        "description": data.description,
        "primary_metric_name": template.primary_metric_name,
        "primary_metric_unit": template.primary_metric_unit,
        "initial_value": data.initial_value,
        "target_value": data.target_value,
        "target_date": data.target_date,
        "direction": direction,  # Store direction on goal for easy access
        "status": "active",
        "ai_context": {
            "summary": "",
            "plan_philosophy": "",
            "current_phase": "building_foundation",
            "next_review_date": None,
        },
        "questionnaire_responses": data.questionnaire_responses,
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.goals.insert_one(doc)
    doc["_id"] = result.inserted_id
    goal = doc_id(doc)

    # Auto-create primary tracker
    from app.services import tracker_service
    from app.models.tracker import TrackerCreate

    primary_tracker = TrackerCreate(
        goal_id=goal["id"],
        name=template.primary_metric_name,
        description=f"Primary metric for {template.name}",
        unit=template.primary_metric_unit,
        type="main",
        direction=direction,  # Use direction calculated above
        is_primary=True
    )
    tracker = await tracker_service.create_tracker(primary_tracker, user_id)

    # Log initial_value as first tracker data point if provided
    if data.initial_value is not None:
        from app.services import daily_log_service
        from app.models.daily_log import TrackerLogInput
        from datetime import date

        today = date.today().isoformat()
        await daily_log_service.log_tracker(
            user_id=user_id,
            goal_id=goal["id"],
            date=today,
            tracker_id=tracker["id"],
            data=TrackerLogInput(value=data.initial_value)
        )

    return goal


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
