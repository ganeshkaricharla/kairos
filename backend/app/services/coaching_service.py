from datetime import timedelta

from bson import ObjectId

from app.database import get_db
from app.models.coaching import PerformanceSnapshot, HabitPerformance, TrackerTrend
from app.services import (
    habit_service,
    tracker_service,
    daily_log_service,
    goal_service,
    ai_service,
    tag_parser,
)
from app.models.habit import HabitCreate, HabitUpdate
from app.models.tracker import TrackerCreate
from app.utils.object_id import doc_id
from app.utils.dates import now, today_str, days_ago, date_range


async def build_performance_snapshot(
    goal_id: str, user_id: str, period_days: int = 3
) -> PerformanceSnapshot:
    end = today_str()
    start_date = days_ago(period_days)
    start = start_date.isoformat()
    dates = date_range(start_date, days_ago(0))

    habits = await habit_service.list_habits(goal_id, status="active")
    logs = await daily_log_service.get_logs_for_period(user_id, goal_id, start, end)

    completions_by_date = {}
    entries_by_date = {}
    for log in logs:
        completions_by_date[log["date"]] = {
            c["habit_id"]: c["completed"]
            for c in log.get("habit_completions", [])
        }
        entries_by_date[log["date"]] = {
            e["tracker_id"]: e["value"]
            for e in log.get("tracker_entries", [])
        }

    habit_perfs = []
    for h in habits:
        completed = sum(
            1
            for d in dates
            if completions_by_date.get(d, {}).get(h["id"], False)
        )
        total = len(dates)
        rate = completed / total if total > 0 else 0
        habit_perfs.append(
            HabitPerformance(
                habit_id=h["id"],
                title=h["title"],
                completed_count=completed,
                total_days=total,
                rate=round(rate, 2),
            )
        )

    trackers = await tracker_service.list_trackers(goal_id)
    tracker_trends = []
    for t in trackers:
        values = [
            entries_by_date.get(d, {}).get(t["id"])
            for d in dates
        ]
        values = [v for v in values if v is not None]
        trend = "stable"
        if len(values) >= 2:
            if values[-1] > values[0]:
                trend = "increasing"
            elif values[-1] < values[0]:
                trend = "decreasing"
        tracker_trends.append(
            TrackerTrend(
                tracker_id=t["id"],
                name=t["name"],
                values=values,
                trend=trend,
            )
        )

    return PerformanceSnapshot(
        period_start=start,
        period_end=end,
        habits=habit_perfs,
        tracker_trends=tracker_trends,
    )


async def start_coaching_session(
    goal_id: str, trigger: str = "scheduled_review", user_id: str = ""
) -> dict:
    db = get_db()

    # Check for existing active session
    existing = await db.coaching_sessions.find_one(
        {"goal_id": goal_id, "status": "active"}
    )
    if existing:
        return doc_id(existing)

    goal = await goal_service.get_goal(goal_id)

    if trigger == "goal_setup":
        # Conversational opening — AI asks questions, no habits yet
        opening = await ai_service.goal_setup_opening(
            title=goal["title"],
            description=goal["description"],
            target_date=goal.get("target_date"),
            user_id=user_id,
        )

        session_doc = {
            "goal_id": goal_id,
            "user_id": user_id,
            "trigger": trigger,
            "status": "active",
            "performance_snapshot": {},
            "messages": [
                {
                    "role": "assistant",
                    "content": opening.message,
                    "timestamp": now(),
                }
            ],
            "proposed_changes": [
                {**c.model_dump(), "accepted": None}
                for c in opening.proposed_changes
            ],
            "created_at": now(),
            "resolved_at": None,
        }
    else:
        # Scheduled review — evaluate performance
        snapshot = await build_performance_snapshot(goal_id, user_id)

        habits_summary = "\n".join(
            f"- {h.title}: {h.completed_count}/{h.total_days} days ({int(h.rate * 100)}%)"
            for h in snapshot.habits
        ) or "No active habits yet."

        tracker_summary = "\n".join(
            f"- {t.name}: values={t.values}, trend={t.trend}"
            for t in snapshot.tracker_trends
        ) or "No tracker data yet."

        evaluation = await ai_service.evaluate_progress(
            goal_title=goal["title"],
            goal_description=goal["description"],
            current_phase=goal["ai_context"]["current_phase"],
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
            habits_summary=habits_summary,
            tracker_summary=tracker_summary,
            user_id=user_id,
        )

        session_doc = {
            "goal_id": goal_id,
            "user_id": user_id,
            "trigger": trigger,
            "status": "active",
            "performance_snapshot": snapshot.model_dump(),
            "messages": [
                {
                    "role": "assistant",
                    "content": evaluation.coaching_message,
                    "timestamp": now(),
                }
            ],
            "proposed_changes": [
                {**c.model_dump(), "accepted": None}
                for c in evaluation.proposed_changes
            ],
            "created_at": now(),
            "resolved_at": None,
        }

    result = await db.coaching_sessions.insert_one(session_doc)
    session_doc["_id"] = result.inserted_id

    # Update next review date
    next_review = (days_ago(0) + timedelta(days=3)).isoformat()
    ai_context = goal["ai_context"]
    ai_context["next_review_date"] = next_review
    await goal_service.update_goal_ai_context(goal_id, ai_context)

    return doc_id(session_doc)


async def get_active_session(goal_id: str) -> dict | None:
    db = get_db()
    doc = await db.coaching_sessions.find_one(
        {"goal_id": goal_id, "status": "active"}
    )
    return doc_id(doc) if doc else None


async def send_message(session_id: str, user_message: str) -> dict:
    db = get_db()
    session = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    goal = await goal_service.get_goal(session["goal_id"])

    # Add user message
    session["messages"].append(
        {"role": "user", "content": user_message, "timestamp": now()}
    )

    # Build context for AI
    snapshot = session.get("performance_snapshot", {})
    habits_summary = "\n".join(
        f"- {h['title']}: {h['completed_count']}/{h['total_days']} ({int(h['rate'] * 100)}%)"
        for h in snapshot.get("habits", [])
    )
    tracker_summary = "\n".join(
        f"- {t['name']}: {t['values']}, trend={t['trend']}"
        for t in snapshot.get("tracker_trends", [])
    )
    performance_summary = f"Habits:\n{habits_summary}\n\nTrackers:\n{tracker_summary}" if habits_summary or tracker_summary else "No data yet (new goal)."

    # Build active habits + trackers context
    active_habits = await habit_service.list_habits(session["goal_id"], status="active")
    active_trackers = await tracker_service.list_trackers(session["goal_id"])

    habits_lines = []
    for h in active_habits:
        line = f"- {h['title']} (ID: {h['id']}, difficulty: {h['difficulty']})"
        if h.get("linked_tracker_id"):
            line += f" [linked to tracker {h['linked_tracker_id']}, threshold: {h.get('tracker_threshold')}]"
        habits_lines.append(line)

    trackers_lines = [
        f"- {t['name']} (ID: {t['id']}, unit: {t['unit']}, direction: {t['direction']})"
        for t in active_trackers
    ]

    active_habits_trackers = (
        f"Active Habits:\n" + ("\n".join(habits_lines) or "None yet.")
        + f"\n\nActive Trackers:\n" + ("\n".join(trackers_lines) or "None yet.")
    )

    pending = [
        c for c in session.get("proposed_changes", []) if c.get("accepted") is None
    ]
    pending_str = "\n".join(f"- {c['description']}" for c in pending) or "None"

    chat_history = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in session["messages"][:-1]
    )

    reply = await ai_service.coaching_reply_ai(
        goal_title=goal["title"],
        current_phase=goal["ai_context"]["current_phase"],
        performance_summary=performance_summary,
        active_habits_trackers=active_habits_trackers,
        pending_changes=pending_str,
        chat_history=chat_history,
        user_message=user_message,
        user_id=session["user_id"],
    )

    # Parse and execute tags from AI response
    clean_message, executed_actions = await tag_parser.parse_and_execute_tags(
        message=reply.message,
        goal_id=session["goal_id"],
        user_id=session["user_id"]
    )

    # Store clean message (with tags removed)
    session["messages"].append(
        {
            "role": "assistant",
            "content": clean_message,
            "timestamp": now(),
            "executed_actions": executed_actions  # Store metadata about tag executions
        }
    )

    # Add any new proposed changes (for backward compatibility, though we're using tags-only)
    for change in reply.proposed_changes:
        session["proposed_changes"].append(
            {**change.model_dump(), "accepted": None}
        )

    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": {
                "messages": session["messages"],
                "proposed_changes": session["proposed_changes"],
                "updated_at": now(),
            }
        },
    )

    updated = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(updated)


async def accept_change(session_id: str, change_index: int) -> dict:
    db = get_db()
    session = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    changes = session["proposed_changes"]
    if change_index >= len(changes):
        raise ValueError("Invalid change index")

    change = changes[change_index]
    change["accepted"] = True

    # Apply the change
    await _apply_change(session["goal_id"], change, session["user_id"])

    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"proposed_changes": changes, "updated_at": now()}},
    )

    updated = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(updated)


async def reject_change(session_id: str, change_index: int) -> dict:
    db = get_db()
    session = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    changes = session["proposed_changes"]
    if change_index >= len(changes):
        raise ValueError("Invalid change index")

    changes[change_index]["accepted"] = False

    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"proposed_changes": changes, "updated_at": now()}},
    )

    updated = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(updated)


async def resolve_session(session_id: str) -> dict:
    db = get_db()
    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "resolved", "resolved_at": now()}},
    )
    doc = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(doc)


async def _apply_change(goal_id: str, change: dict, user_id: str):
    change_type = change["type"]
    details = change.get("details", {})

    if change_type == "add_habit":
        # If AI included tracker details, create the linked tracker first
        linked_tracker_id = None
        tracker_threshold = details.get("tracker_threshold")
        tracker_name = details.get("tracker_name")

        if tracker_name:
            tracker = await tracker_service.create_tracker(
                TrackerCreate(
                    goal_id=goal_id,
                    name=tracker_name,
                    unit=details.get("tracker_unit", ""),
                    direction=details.get("tracker_direction", "increase"),
                    reasoning=details.get("reasoning", ""),
                    type="supporting",
                ),
                user_id=user_id,
            )
            linked_tracker_id = tracker["id"]

        await habit_service.create_habit(
            HabitCreate(
                goal_id=goal_id,
                title=details.get("title", "New Habit"),
                description=details.get("description", ""),
                frequency=details.get("frequency", "daily"),
                difficulty=details.get("difficulty", "easy"),
                reasoning=details.get("reasoning", ""),
                status="active",
                linked_tracker_id=linked_tracker_id,
                tracker_threshold=tracker_threshold,
            ),
            user_id=user_id,
        )

    elif change_type == "swap_habit":
        old_id = details.get("old_habit_id")
        if old_id:
            new_habit = await habit_service.create_habit(
                HabitCreate(
                    goal_id=goal_id,
                    title=details.get("new_title", "New Habit"),
                    description=details.get("new_description", ""),
                    difficulty=details.get("difficulty", "easy"),
                    reasoning=details.get("reasoning", ""),
                    status="active",
                ),
                user_id=user_id,
            )
            await habit_service.update_habit(
                old_id,
                HabitUpdate(status="swapped", replaced_by=new_habit["id"]),
            )

    elif change_type == "pause_habit":
        habit_id = details.get("habit_id")
        if habit_id:
            await habit_service.update_habit(
                habit_id, HabitUpdate(status="paused")
            )

    elif change_type == "add_tracker":
        await tracker_service.create_tracker(
            TrackerCreate(
                goal_id=goal_id,
                name=details.get("name", "New Tracker"),
                unit=details.get("unit", ""),
                direction=details.get("direction", "increase"),
                reasoning=details.get("reasoning", ""),
                type="supporting",
            ),
            user_id=user_id,
        )
