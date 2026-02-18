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


async def enrich_habits_with_stats(habits: list[dict], goal_id: str, user_id: str) -> list[dict]:
    """
    Enrich habit documents with computed statistics expected by prompt_builder.
    Adds: is_formed, formation_count, current_streak, best_streak, completion_last_7_days, completed_today
    """
    if not habits:
        return []

    # Fetch last 14 days of logs for statistics
    end_date = days_ago(0).isoformat()
    start_date = days_ago(13).isoformat()
    logs = await daily_log_service.get_logs_for_period(user_id, goal_id, start_date, end_date)

    # Get today's date string
    today = days_ago(0).isoformat()

    enriched_habits = []
    for habit in habits:
        habit_id = habit["id"]

        # Get all completions for this habit
        all_completions = []
        for log in logs:
            for completion in log.get("habit_completions", []):
                if completion["habit_id"] == habit_id and completion.get("completed"):
                    all_completions.append({
                        "date": log["date"],
                        "completed": True
                    })

        # Calculate formation count (total completions ever)
        formation_count = len(all_completions)
        is_formed = formation_count >= 8

        # Calculate current streak (consecutive days from today backwards)
        current_streak = 0
        dates_last_14 = [days_ago(i).isoformat() for i in range(14)]
        dates_last_14.reverse()  # Start from oldest to newest

        for i in range(len(dates_last_14) - 1, -1, -1):  # Go backwards from today
            date = dates_last_14[i]
            completed = any(c["date"] == date for c in all_completions)
            if completed:
                current_streak += 1
            else:
                if i == len(dates_last_14) - 1:  # Today not done
                    break
                else:  # Streak broken
                    break

        # Calculate best streak (not implemented - would need full history)
        best_streak = current_streak  # Simplified for now

        # Count completions in last 7 days
        last_7_dates = [days_ago(i).isoformat() for i in range(7)]
        completion_last_7_days = sum(1 for c in all_completions if c["date"] in last_7_dates)

        # Check if completed today
        completed_today = any(c["date"] == today for c in all_completions)

        # Add computed fields to habit
        enriched_habit = {
            **habit,
            "is_formed": is_formed,
            "formation_count": formation_count,
            "current_streak": current_streak,
            "best_streak": best_streak,
            "completion_last_7_days": completion_last_7_days,
            "completed_today": completed_today,
        }
        enriched_habits.append(enriched_habit)

    return enriched_habits


async def start_coaching_session(
    goal_id: str, trigger: str = "scheduled_review", user_id: str = ""
) -> dict:
    from app.config import settings
    from datetime import datetime

    db = get_db()

    # Check for existing active session
    existing = await db.coaching_sessions.find_one(
        {"goal_id": goal_id, "status": "active"}
    )
    if existing:
        return doc_id(existing)

    goal = await goal_service.get_goal(goal_id)

    # Check if session is locked
    if settings.session_lock_enabled:
        ai_context = goal.get("ai_context") or {}
        next_allowed = ai_context.get("next_session_allowed_at")
        if next_allowed:
            # Parse the datetime
            if isinstance(next_allowed, str):
                next_allowed_dt = datetime.fromisoformat(next_allowed.replace('Z', '+00:00'))
            else:
                next_allowed_dt = next_allowed

            if datetime.utcnow() < next_allowed_dt.replace(tzinfo=None):
                # Session is still locked
                hours_remaining = (next_allowed_dt.replace(tzinfo=None) - datetime.utcnow()).total_seconds() / 3600
                raise ValueError(
                    f"Chat is locked. You can start a new session in {int(hours_remaining)} hours and {int((hours_remaining % 1) * 60)} minutes."
                )

    # Fetch previous session summaries (last 3 resolved sessions)
    previous_sessions = await db.coaching_sessions.find(
        {"goal_id": goal_id, "status": "resolved"}
    ).sort("resolved_at", -1).limit(3).to_list(length=3)

    previous_summaries = []
    for prev_session in previous_sessions:
        summary = prev_session.get("summary", {})
        if summary and summary.get("key_points"):
            previous_summaries.append({
                "date": prev_session.get("resolved_at", ""),
                "key_points": summary.get("key_points", []),
                "habits_added": summary.get("habits_added", []),
                "action_items": summary.get("action_items", []),
            })

    # Format previous summaries if any exist
    summaries_text = ""
    if previous_summaries:
        summaries_text = "📝 **Previous Chat Summaries:**\n\n"
        for i, summary in enumerate(previous_summaries, 1):
            date_str = summary["date"]
            if isinstance(date_str, str):
                try:
                    from datetime import datetime as dt
                    date_obj = dt.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime("%B %d, %Y")
                except:
                    pass

            summaries_text += f"**Session {i}** ({date_str}):\n"
            if summary.get("key_points"):
                summaries_text += "- " + "\n- ".join(summary["key_points"]) + "\n"
            if summary.get("habits_added"):
                summaries_text += f"Habits added: {', '.join(summary['habits_added'])}\n"
            summaries_text += "\n"

        summaries_text += "---\n\n"

    if trigger == "goal_setup":
        # Use Prompt #1 (Initial Session) - Per integration guide section 3
        from app.services import user_service

        user = await user_service.get_user(user_id)

        # Initial session starts in exploring phase
        response = await ai_service.initial_session_reply(
            user=user,
            goal=goal,
            conversation_history="",  # First turn, Priya speaks first
            current_phase="exploring",
            questionnaire_responses=goal.get("questionnaire_responses", {}),
            template_id=goal.get("template_id"),
        )

        # Prepend summaries to the message (if any from previous goals)
        message_content = summaries_text + response["message"]

        session_doc = {
            "goal_id": goal_id,
            "user_id": user_id,
            "trigger": trigger,
            "status": "active",
            "performance_snapshot": {},
            "initial_session_phase": response["phase"],  # Track phase state
            "messages": [
                {
                    "role": "assistant",
                    "content": message_content,
                    "timestamp": now(),
                }
            ],
            "created_at": now(),
            "resolved_at": None,
        }
    else:
        # Review session (Prompt #4) - Per integration guide section 6
        from app.services import user_service

        user = await user_service.get_user(user_id)
        habits = await habit_service.list_habits(goal_id, status="active")
        trackers = await tracker_service.list_trackers(goal_id)

        # Determine trigger type and reason
        if trigger == "scheduled_review":
            trigger_type = "scheduled"
            trigger_reason = "Regular weekly check-in"
        else:
            # Could be other types: streak_broken, consistently_missing, etc.
            trigger_type = trigger
            trigger_reason = f"{trigger.replace('_', ' ').title()} detected"

        # Use Prompt #4 (Review Session)
        response = await ai_service.review_session_reply(
            user=user,
            goal=goal,
            habits=habits,
            trackers=trackers,
            conversation_history="",  # First turn, Priya speaks first
            trigger_type=trigger_type,
            trigger_reason=trigger_reason,
            review_stage="opening",
        )

        # Prepend summaries to the message
        message_content = summaries_text + response["message"]

        session_doc = {
            "goal_id": goal_id,
            "user_id": user_id,
            "trigger": trigger,
            "status": "active",
            "review_active": True,  # Mark as review session
            "review_stage": "opening",  # Track review stage
            "review_trigger_type": trigger_type,
            "review_trigger_reason": trigger_reason,
            "performance_snapshot": {},
            "messages": [
                {
                    "role": "assistant",
                    "content": message_content,
                    "timestamp": now(),
                }
            ],
            "created_at": now(),
            "resolved_at": None,
        }

    result = await db.coaching_sessions.insert_one(session_doc)
    session_doc["_id"] = result.inserted_id

    # Update next review date
    next_review = (days_ago(0) + timedelta(days=3)).isoformat()
    ai_context = goal.get("ai_context") or {}
    ai_context["next_review_date"] = next_review
    await goal_service.update_goal_ai_context(goal_id, ai_context)

    return doc_id(session_doc)


async def get_active_session(goal_id: str) -> dict | None:
    db = get_db()
    doc = await db.coaching_sessions.find_one(
        {"goal_id": goal_id, "status": "active"}
    )
    return doc_id(doc) if doc else None


async def detect_review_trigger(user_id: str, goal_id: str) -> tuple[str, str] | None:
    """
    Detect if a review session should be triggered.
    Per integration guide section 6 (Prompt #4).

    Returns:
        tuple[trigger_type, trigger_reason] if review needed, None otherwise
    """
    from datetime import date as dt_date

    goal = await goal_service.get_goal(goal_id)
    habits = await habit_service.list_habits(goal_id, status="active")

    # Check 1: Scheduled review (7 days since last review)
    last_review_str = goal.get("ai_context", {}).get("last_review_date")
    if last_review_str:
        try:
            last_review = dt_date.fromisoformat(last_review_str)
            days_since = (dt_date.today() - last_review).days
            if days_since >= 7:
                return ("scheduled", "Regular weekly check-in")
        except:
            pass
    else:
        # Never had a review - check if goal is at least 7 days old
        created_at = goal.get("created_at", "")
        try:
            created_date = dt_date.fromisoformat(created_at.split("T")[0])
            days_since_created = (dt_date.today() - created_date).days
            if days_since_created >= 7:
                return ("scheduled", "First weekly check-in")
        except:
            pass

    # Check 2: Streak broken (5+ day streak missed)
    for habit in habits:
        streak_before = habit.get("streak_before_last_miss", 0)
        consecutive_missed = habit.get("consecutive_missed", 0)
        if consecutive_missed >= 1 and streak_before >= 5:
            return ("streak_broken", f"You had a {streak_before}-day streak on '{habit['title']}' that just broke")

    # Check 3: Consistently missing (3+ days)
    for habit in habits:
        consecutive_missed = habit.get("consecutive_missed", 0)
        if consecutive_missed >= 3:
            return ("consistently_missing", f"Missed '{habit['title']}' for {consecutive_missed} days in a row")

    # Check 4: Breakthrough (habit just formed)
    for habit in habits:
        formation_count = habit.get("formation_count", 0)
        if formation_count == 8 and not habit.get("formation_celebrated", False):
            return ("breakthrough", f"You just formed '{habit['title']}' - 8 completions reached!")

    # TODO: Add more trigger types:
    # - target_at_risk (pace slipping)
    # - plateau (metric flat 10+ days)

    return None


async def send_message(session_id: str, user_message: str) -> dict:
    """
    Send a message in a coaching session.
    Routes to appropriate prompt based on session state (per integration guide).
    """
    from app.services import user_service

    db = get_db()
    session = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    goal = await goal_service.get_goal(session["goal_id"])
    user = await user_service.get_user(session["user_id"])

    # Add user message to session
    session["messages"].append(
        {"role": "user", "content": user_message, "timestamp": now()}
    )

    # Format chat history (include ALL messages including the one just added)
    chat_history = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in session["messages"]
    )

    # Decision tree: Which prompt fires? (per integration guide section 2)

    # Check if this is an initial session (Prompt #1)
    if session.get("initial_session_phase") and session["initial_session_phase"] != "complete":
        # Use Prompt #1 (Initial Session)
        response = await ai_service.initial_session_reply(
            user=user,
            goal=goal,
            conversation_history=chat_history,
            current_phase=session.get("initial_session_phase", "exploring"),
            questionnaire_responses=goal.get("questionnaire_responses", {}),
            template_id=goal.get("template_id"),
        )

        # Update phase
        session["initial_session_phase"] = response["phase"]
        reply_message = response["message"]

        # Note: Initial session returns {phase, message}, not CoachingReply
        # So we wrap it in a compatible format
        from app.models.ai import CoachingReply
        reply = CoachingReply(message=reply_message, tool_calls=[])

    # Check if this is a review session (Prompt #4)
    elif session.get("review_active"):
        # Use Prompt #4 (Review Session)
        habits = await habit_service.list_habits(session["goal_id"], status="active")
        trackers = await tracker_service.list_trackers(session["goal_id"])

        # Enrich habits with computed statistics
        habits = await enrich_habits_with_stats(habits, session["goal_id"], session["user_id"])

        # Advance review stage if needed
        review_stage = session.get("review_stage", "opening")
        if len(session["messages"]) > 2 and review_stage == "opening":
            review_stage = "mid_conversation"
            session["review_stage"] = review_stage

        response = await ai_service.review_session_reply(
            user=user,
            goal=goal,
            habits=habits,
            trackers=trackers,
            conversation_history=chat_history,
            trigger_type=session.get("review_trigger_type", "scheduled"),
            trigger_reason=session.get("review_trigger_reason", "Regular weekly check-in"),
            review_stage=review_stage,
        )

        reply_message = response["message"]

        # Wrap in CoachingReply format
        from app.models.ai import CoachingReply
        reply = CoachingReply(message=reply_message, tool_calls=[])

    else:
        # Use Prompt #2 (Regular Coaching System Prompt Builder)
        habits = await habit_service.list_habits(session["goal_id"], status="active")
        trackers = await tracker_service.list_trackers(session["goal_id"])

        # Enrich habits with computed statistics
        habits = await enrich_habits_with_stats(habits, session["goal_id"], session["user_id"])

        # DEBUG: Log what we're fetching
        print(f"[DEBUG] Fetched {len(habits)} habits and {len(trackers)} trackers for goal {session['goal_id']}")
        if habits:
            print(f"[DEBUG] Habits: {[h['title'] for h in habits]}")
            print(f"[DEBUG] Habit stats: {[(h['title'], h.get('formation_count', 0), h.get('is_formed', False)) for h in habits]}")
        if trackers:
            print(f"[DEBUG] Trackers: {[t['name'] for t in trackers]}")

        # Get today's logs
        today_date = days_ago(0).isoformat()
        today_logs = await daily_log_service.get_or_create_log(
            session["user_id"],
            session["goal_id"],
            today_date
        ) or {}

        # TODO: Add upcoming_checkins from calendar/scheduling system
        upcoming_checkins = []

        reply = await ai_service.coaching_reply_ai(
            user=user,
            goal=goal,
            habits=habits,
            trackers=trackers,
            today_logs=today_logs,
            chat_history=chat_history,
            user_message=user_message,
            upcoming_checkins=upcoming_checkins,
            use_tools=True,  # Enable AI function calling
        )

    # Check if AI decided not to reply
    if reply.message.strip() == "NO NEED TO REPLY":
        # Remove the user's message from history (no response needed)
        session["messages"].pop()

        # Update session without adding AI response
        await db.coaching_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "messages": session["messages"],
                    "updated_at": now(),
                }
            },
        )

        updated = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
        result = doc_id(updated)
        # Add a flag to indicate no reply was needed
        result["no_reply_needed"] = True
        return result

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
            "executed_actions": executed_actions,  # Store metadata about tag executions
            "tool_calls": reply.tool_calls  # Store tool calls made by AI (for UI display)
        }
    )

    # Build update dict with messages and updated_at
    update_data = {
        "messages": session["messages"],
        "updated_at": now(),
    }

    # Include phase tracking if it exists
    if "initial_session_phase" in session:
        update_data["initial_session_phase"] = session["initial_session_phase"]
    if "review_stage" in session:
        update_data["review_stage"] = session["review_stage"]

    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": update_data},
    )

    updated = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(updated)


async def resolve_session(session_id: str) -> dict:
    """Resolve a coaching session and generate a summary."""
    from app.config import settings
    from datetime import datetime

    db = get_db()

    # Get session data first
    session = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    # Get goal for context
    goal = await goal_service.get_goal(session["goal_id"])

    # Format chat history for summary
    chat_history = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in session.get("messages", [])
    ])

    # Generate summary using AI
    try:
        summary_data = await ai_service.generate_session_summary(
            goal_title=goal.get("title", "Your goal"),
            chat_history=chat_history,
            user_id=session.get("user_id"),
        )
    except Exception as e:
        # If summary generation fails, use a basic fallback
        summary_data = {
            "key_points": ["Coaching session completed"],
            "habits_added": [],
            "next_check_in": None,
            "action_items": ["Continue tracking your habits"],
        }

    # Update session with summary and mark as resolved
    await db.coaching_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": {
                "status": "resolved",
                "resolved_at": now(),
                "summary": summary_data,
            }
        },
    )

    # Set session lock on goal if enabled
    if settings.session_lock_enabled:
        lock_until = datetime.utcnow() + timedelta(hours=settings.session_lock_hours)
        ai_context = goal.get("ai_context") or {}
        ai_context["next_session_allowed_at"] = lock_until
        await goal_service.update_goal_ai_context(session["goal_id"], ai_context)

    doc = await db.coaching_sessions.find_one({"_id": ObjectId(session_id)})
    return doc_id(doc)


async def detect_proactive_trigger(user_id: str, goal_id: str) -> dict | None:
    """
    Detect if a proactive check-in should be triggered.
    Per integration guide section 7 (Prompt #5).

    Returns:
        dict with trigger_type and trigger_details if needed, None otherwise
    """
    habits = await habit_service.list_habits(goal_id, status="active")
    trackers = await tracker_service.list_trackers(goal_id)
    goal = await goal_service.get_goal(goal_id)

    # Priority 1: Missed 3+ days (most urgent)
    for habit in habits:
        consecutive_missed = habit.get("consecutive_missed", 0)
        if consecutive_missed >= 3:
            return {
                "type": "missed_3_plus_days",
                "details": {
                    "habit_id": habit["id"],
                    "habit_title": habit["title"],
                    "days_missed": consecutive_missed,
                }
            }

    # Priority 2: Habit just formed (celebration)
    for habit in habits:
        formation_count = habit.get("formation_count", 0)
        is_formed = habit.get("is_formed", False)
        formation_celebrated = habit.get("formation_celebrated", False)

        if is_formed and formation_count >= 8 and not formation_celebrated:
            return {
                "type": "habit_formed",
                "details": {
                    "habit_id": habit["id"],
                    "habit_title": habit["title"],
                    "formation_count": formation_count,
                }
            }

    # Priority 3: Metric moving wrong direction
    # TODO: Implement metric trend detection
    # Would need to:
    # 1. Get primary tracker from goal
    # 2. Calculate 7-day trend
    # 3. Check if moving opposite to desired direction
    # 4. Detect context flags from memories

    return None


async def generate_proactive_message(user_id: str, goal_id: str) -> dict | None:
    """
    Generate and store a proactive check-in message.
    Per integration guide section 7.

    Returns:
        dict with message details if generated, None if no trigger
    """
    from app.services import user_service

    # Check if trigger exists
    trigger = await detect_proactive_trigger(user_id, goal_id)
    if not trigger:
        return None

    # Get context data
    user = await user_service.get_user(user_id)
    goal = await goal_service.get_goal(goal_id)
    habits = await habit_service.list_habits(goal_id, status="active")
    trackers = await tracker_service.list_trackers(goal_id)

    # Generate proactive message
    response = await ai_service.proactive_checkin_reply(
        user=user,
        goal=goal,
        habits=habits,
        trackers=trackers,
        trigger_type=trigger["type"],
        trigger_details=trigger["details"],
    )

    # Store as pending message
    db = get_db()
    pending_doc = {
        "user_id": user_id,
        "goal_id": goal_id,
        "trigger_type": response["trigger_type"],
        "delivery": response["delivery"],
        "message": response["message"],
        "created_at": now(),
        "delivered": False,
    }

    result = await db.pending_proactive_messages.insert_one(pending_doc)

    # Mark habit as celebrated if it was a formation trigger
    if trigger["type"] == "habit_formed":
        habit_id = trigger["details"]["habit_id"]
        await habit_service.mark_formation_celebrated(habit_id)

    return {
        "id": str(result.inserted_id),
        "trigger_type": response["trigger_type"],
        "delivery": response["delivery"],
        "message": response["message"],
    }


async def get_pending_proactive_messages(user_id: str, goal_id: str) -> list[dict]:
    """
    Get all pending proactive messages for a user/goal.
    These are shown when user opens the app.
    """
    db = get_db()
    cursor = db.pending_proactive_messages.find({
        "user_id": user_id,
        "goal_id": goal_id,
        "delivered": False,
    })

    messages = []
    async for doc in cursor:
        messages.append({
            "id": str(doc["_id"]),
            "trigger_type": doc["trigger_type"],
            "message": doc["message"],
            "created_at": doc["created_at"],
        })

    return messages


async def mark_proactive_message_delivered(message_id: str):
    """Mark a proactive message as delivered."""
    db = get_db()
    await db.pending_proactive_messages.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"delivered": True, "delivered_at": now()}}
    )


