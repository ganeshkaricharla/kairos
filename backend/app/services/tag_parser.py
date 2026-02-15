"""Tag parser for extracting and executing actions from AI responses."""
import re
import json
import logging
from typing import Tuple, List
from datetime import datetime

from app.services import user_service
from app.utils.dates import today_str, now


logger = logging.getLogger(__name__)


async def parse_and_execute_tags(
    message: str,
    goal_id: str,
    user_id: str
) -> Tuple[str, List[dict]]:
    """
    Parse tags from AI message, execute actions, return clean message.

    Supported tags:
    - [HABIT]{...}[/HABIT] - Create habit
    - [TRACKER]{...}[/TRACKER] - Create tracker
    - [LOG]{"key": "name", "value": 123}[/LOG] - Log tracker data
    - [MEMORY]{"text": "...", "type": "preference"}[/MEMORY] - Save memory
    - [DELETE_HABIT]{"habit_id": "..."}[/DELETE_HABIT] - Delete habit
    - [UPDATE_HABIT]{...}[/UPDATE_HABIT] - Update habit

    Args:
        message: AI response message with potential tags
        goal_id: Goal ID for context
        user_id: User ID for context

    Returns:
        Tuple of (clean_message, executed_actions)
        - clean_message: Message with tags removed
        - executed_actions: List of {type, data, success, error} dicts
    """
    executed_actions = []
    clean_msg = message

    # Parse and execute each tag type
    tag_types = [
        ("HABIT", _create_habit_from_tag),
        ("TRACKER", _create_tracker_from_tag),
        ("LOG", _log_tracker_from_tag),
        ("MEMORY", _save_memory_from_tag),
        ("DELETE_HABIT", _delete_habit_from_tag),
        ("UPDATE_HABIT", _update_habit_from_tag),
    ]

    for tag_name, executor_func in tag_types:
        pattern = rf'\[{tag_name}\](.*?)\[/{tag_name}\]'
        matches = list(re.finditer(pattern, clean_msg, re.DOTALL))

        for match in matches:
            try:
                # Parse JSON data
                data = json.loads(match.group(1).strip())

                # Execute action
                if tag_name in ("MEMORY",):
                    # Memory doesn't need goal_id
                    result = await executor_func(data, user_id)
                else:
                    result = await executor_func(data, goal_id, user_id)

                executed_actions.append({
                    "type": tag_name,
                    "data": data,
                    "success": True,
                    "result": result
                })

                # Remove tag from message
                clean_msg = clean_msg.replace(match.group(0), '')

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {tag_name} tag JSON: {e}")
                executed_actions.append({
                    "type": tag_name,
                    "data": match.group(1).strip(),
                    "success": False,
                    "error": f"Invalid JSON: {str(e)}"
                })

            except Exception as e:
                logger.error(f"Failed to execute {tag_name} tag: {e}")
                executed_actions.append({
                    "type": tag_name,
                    "data": match.group(1).strip(),
                    "success": False,
                    "error": str(e)
                })

    # Clean up extra whitespace
    clean_msg = re.sub(r'\n{3,}', '\n\n', clean_msg).strip()

    return clean_msg, executed_actions


async def _create_habit_from_tag(data: dict, goal_id: str, user_id: str) -> dict:
    """
    Create habit from [HABIT] tag.

    Expected data format:
    {
        "title": "Habit name",
        "description": "What to do",
        "difficulty": "easy",
        "frequency": "daily",
        "linked_tracker_id": "optional_tracker_id",
        "tracker_threshold": 10000
    }
    """
    from app.services import habit_service
    from app.models.habit import HabitCreate

    habit_data = HabitCreate(
        goal_id=goal_id,
        title=data["title"],
        description=data.get("description", ""),
        difficulty=data.get("difficulty", "easy"),
        frequency=data.get("frequency", "daily"),
        time_of_day=data.get("time_of_day"),
        duration_minutes=data.get("duration_minutes"),
        reasoning=data.get("reasoning", ""),
        status="active",
        order=data.get("order", 0),
        linked_tracker_id=data.get("linked_tracker_id"),
        tracker_threshold=data.get("tracker_threshold")
    )

    habit = await habit_service.create_habit(habit_data, user_id)
    logger.info(f"Created habit via tag: {habit['title']} (id: {habit['id']})")
    return habit


async def _create_tracker_from_tag(data: dict, goal_id: str, user_id: str) -> dict:
    """
    Create tracker from [TRACKER] tag.

    Expected data format:
    {
        "name": "Tracker name",
        "unit": "unit",
        "type": "supporting",
        "direction": "increase",
        "target_value": 10000
    }
    """
    from app.services import tracker_service
    from app.models.tracker import TrackerCreate

    tracker_data = TrackerCreate(
        goal_id=goal_id,
        name=data["name"],
        description=data.get("description", ""),
        unit=data.get("unit", ""),
        type=data.get("type", "supporting"),
        direction=data.get("direction", "increase"),
        target_value=data.get("target_value"),
        reasoning=data.get("reasoning", "")
    )

    tracker = await tracker_service.create_tracker(tracker_data, user_id)
    logger.info(f"Created tracker via tag: {tracker['name']} (id: {tracker['id']})")
    return tracker


async def _log_tracker_from_tag(data: dict, goal_id: str, user_id: str) -> dict:
    """
    Log tracker value from [LOG] tag.

    Expected data format:
    {
        "key": "tracker_name_or_id",
        "value": 1850
    }
    """
    from app.services import daily_log_service, tracker_service
    from app.models.daily_log import TrackerLogInput

    # Find tracker by name (case-insensitive) or ID
    trackers = await tracker_service.list_trackers(goal_id)
    tracker = None

    # Try to find by name first
    for t in trackers:
        if t["name"].lower() == data["key"].lower():
            tracker = t
            break

    # If not found by name, try ID
    if not tracker:
        for t in trackers:
            if t["id"] == data["key"]:
                tracker = t
                break

    if not tracker:
        raise ValueError(f"Tracker not found: {data['key']}")

    # Log the value
    log_data = TrackerLogInput(
        value=float(data["value"]),
        notes=data.get("notes", "")
    )

    result = await daily_log_service.log_tracker(
        user_id=user_id,
        goal_id=goal_id,
        date=today_str(),
        tracker_id=tracker["id"],
        data=log_data
    )

    logger.info(f"Logged tracker via tag: {tracker['name']} = {data['value']}")
    return {"tracker_id": tracker["id"], "value": data["value"], "log": result}


async def _save_memory_from_tag(data: dict, user_id: str) -> dict:
    """
    Save memory from [MEMORY] tag.

    Expected data format:
    {
        "text": "User prefers morning workouts",
        "type": "preference"
    }
    """
    memory_type = data.get("type", "general")
    user = await user_service.add_memory(user_id, data["text"], memory_type)

    logger.info(f"Saved memory via tag: {data['text'][:50]}...")
    return {"memory_added": True, "type": memory_type}


async def _delete_habit_from_tag(data: dict, goal_id: str, user_id: str) -> dict:
    """
    Delete habit from [DELETE_HABIT] tag.

    Expected data format:
    {
        "habit_id": "habit_id_to_delete"
    }
    """
    from app.services import habit_service

    # Get habit to verify it exists
    habit = await habit_service.get_habit(data["habit_id"])
    if not habit:
        raise ValueError(f"Habit not found: {data['habit_id']}")

    # Update status to deleted/archived instead of hard delete
    from app.models.habit import HabitUpdate
    updated = await habit_service.update_habit(
        data["habit_id"],
        HabitUpdate(status="archived")
    )

    logger.info(f"Archived habit via tag: {habit['title']} (id: {data['habit_id']})")
    return {"habit_id": data["habit_id"], "status": "archived"}


async def _update_habit_from_tag(data: dict, goal_id: str, user_id: str) -> dict:
    """
    Update habit from [UPDATE_HABIT] tag.

    Expected data format:
    {
        "habit_id": "habit_id_to_update",
        "title": "New title",
        "description": "New description",
        ...
    }
    """
    from app.services import habit_service
    from app.models.habit import HabitUpdate

    habit_id = data.pop("habit_id")

    # Build update object from remaining data
    update_data = HabitUpdate(**data)

    updated = await habit_service.update_habit(habit_id, update_data)
    if not updated:
        raise ValueError(f"Habit not found: {habit_id}")

    logger.info(f"Updated habit via tag: {habit_id}")
    return updated
