"""Dynamic system prompt builder for context-aware AI coaching."""
from datetime import datetime
from typing import List, Dict

from app.prompts.personalities import get_personality_prompt
from app.services import daily_log_service
from app.utils.dates import today_str, days_ago


async def build_coaching_system_prompt(
    user: dict,
    goal: dict,
    habits: List[dict],
    trackers: List[dict],
    today_logs: dict
) -> str:
    """
    Build dynamic system prompt with personality, memories, and full context.

    Args:
        user: User document with coaching_style and memories
        goal: Goal document with ai_context
        habits: List of active habit documents
        trackers: List of tracker documents
        today_logs: Today's daily log document

    Returns:
        Complete system prompt string
    """
    sections = []

    # 1. Time-based greeting and focus
    sections.append(_get_time_context(datetime.now().hour))
    sections.append("")

    # 2. Personality injection
    coaching_style = user.get("coaching_style", "balanced")
    personality_prompt = get_personality_prompt(coaching_style)
    sections.append(personality_prompt)
    sections.append("")

    # 3. User memories
    memories_section = _build_memories_section(user.get("memories", []))
    sections.append("## What You Know About the User")
    sections.append(memories_section)
    sections.append("")

    # 4. Current goal
    sections.append("## Current Goal")
    sections.append(_build_goal_section(goal))
    sections.append("")

    # 5. Trackers with today's values + 7-day averages
    sections.append("## Trackers (Metrics Being Measured)")
    trackers_section = await _build_trackers_section(
        trackers, today_logs, goal["id"], user["id"]
    )
    sections.append(trackers_section)
    sections.append("")

    # 6. Habits with formation status + streaks
    sections.append("## Habits (Daily Actions)")
    habits_section = _build_habits_section(habits)
    sections.append(habits_section)
    sections.append("")

    # 7. Your capabilities and behavioral rules
    sections.append("## Your Capabilities and Rules")
    sections.append(_build_instructions(habits))

    return "\n".join(sections)


def _get_time_context(hour: int) -> str:
    """Get time-based greeting and focus area."""
    if 5 <= hour < 8:
        return """**TIME CONTEXT**: Early morning (5-8 AM)
- Greeting: "Good morning"
- Focus: Plan the day. Set intentions. Review morning habits."""

    elif 8 <= hour < 12:
        return """**TIME CONTEXT**: Morning (8 AM - 12 PM)
- Greeting: "Morning"
- Focus: Get started with tracking. Log morning data."""

    elif 12 <= hour < 17:
        return """**TIME CONTEXT**: Afternoon (12-5 PM)
- Greeting: "Hey"
- Focus: Check-in on progress. Address challenges."""

    elif 17 <= hour < 22:
        return """**TIME CONTEXT**: Evening (5-10 PM)
- Greeting: "Evening"
- Focus: Review the day. Complete pending habits. Log missing data."""

    else:
        return """**TIME CONTEXT**: Night (10 PM - 5 AM)
- Greeting: "Hey"
- Focus: Keep it brief. Prep for tomorrow. Quick check-ins only."""


def _build_memories_section(memories: List[dict]) -> str:
    """Format user memories for prompt."""
    if not memories:
        return "No memories saved yet. Learn about the user through conversation."

    # Show last 10 memories
    recent = memories[-10:]
    lines = []
    for m in recent:
        mem_type = m.get("type", "general")
        lines.append(f"- {m['text']} ({mem_type})")

    return "\n".join(lines)


def _build_goal_section(goal: dict) -> str:
    """Format goal information."""
    ai_context = goal.get("ai_context", {})

    lines = [
        f"**Title**: {goal['title']}",
        f"**Description**: {goal['description']}",
        f"**Current Phase**: {ai_context.get('current_phase', 'building_foundation')}",
    ]

    if goal.get("target_date"):
        lines.append(f"**Target Date**: {goal['target_date']}")

    if ai_context.get("plan_philosophy"):
        lines.append(f"**Plan Philosophy**: {ai_context['plan_philosophy']}")

    return "\n".join(lines)


async def _build_trackers_section(
    trackers: List[dict],
    today_logs: dict,
    goal_id: str,
    user_id: str
) -> str:
    """Build trackers section with today's values and 7-day averages."""
    if not trackers:
        return "No trackers yet. Consider suggesting relevant metrics to measure progress."

    lines = []
    tracker_entries = today_logs.get("tracker_entries", []) if today_logs else []

    for tracker in trackers:
        # Today's value
        today_entry = next(
            (e for e in tracker_entries if e["tracker_id"] == tracker["id"]),
            None
        )
        today_value = today_entry["value"] if today_entry else None

        # Calculate 7-day average
        avg_7day = await _calculate_tracker_average(tracker["id"], user_id, goal_id, 7)

        # Format line
        today_str = f"**Today**: {today_value} {tracker['unit']}" if today_value is not None else "**Today**: NOT LOGGED"
        avg_str = f"**7-day avg**: {avg_7day:.1f} {tracker['unit']}" if avg_7day is not None else "**7-day avg**: No data"

        target_str = ""
        if tracker.get("target_value"):
            target_str = f" | **Target**: {tracker['target_value']} {tracker['unit']}"

        lines.append(f"- **{tracker['name']}**: {today_str} | {avg_str}{target_str}")

    return "\n".join(lines)


def _build_habits_section(habits: List[dict]) -> str:
    """Build habits section with formation status and streaks."""
    if not habits:
        return """No habits yet.

**Can add new habit**: Yes (no active habits)"""

    lines = []
    active_habits = [h for h in habits if h.get("status") == "active"]

    # Check if new habits can be added (all active habits must be formed)
    can_add_new = all(h.get("is_formed", False) for h in active_habits)

    for habit in active_habits:
        # Formation status
        formation_count = habit.get("formation_count", 0)
        is_formed = habit.get("is_formed", False)

        if is_formed:
            status = "✓ FORMED"
        else:
            status = f"Building ({formation_count}/8)"

        # Streak
        streak = habit.get("current_streak", 0)
        streak_str = f"**Streak**: {streak} days" if streak > 0 else "**Streak**: None"

        # Best streak
        best = habit.get("best_streak", 0)
        best_str = f"(best: {best})" if best > streak else ""

        # Linked tracker info
        linked_str = ""
        if habit.get("linked_tracker_id"):
            linked_str = f" | **Auto-completes** when tracker >= {habit.get('tracker_threshold')}"

        lines.append(
            f"- **{habit['title']}** (ID: {habit['id']}): {status} | {streak_str} {best_str}{linked_str}"
        )

    lines.append("")
    lines.append(f"**Can add new habit**: {'Yes' if can_add_new else 'No (active habits not yet formed - need 8 completions each)'}")

    return "\n".join(lines)


def _build_instructions(habits: List[dict]) -> str:
    """Build behavioral instructions and tag syntax."""
    return """
**ACTION TAGS** (use these to execute immediate actions):

- `[HABIT]{...}[/HABIT]` - Create new habit
  Example: [HABIT]{"title": "Walk 10k steps", "difficulty": "medium", "linked_tracker_id": "tracker_id", "tracker_threshold": 10000}[/HABIT]

- `[TRACKER]{...}[/TRACKER]` - Create new tracker
  Example: [TRACKER]{"name": "Steps", "unit": "steps", "direction": "increase", "target_value": 10000}[/TRACKER]

- `[LOG]{"key": "tracker_name", "value": 123}[/LOG]` - Log tracker data immediately
  Example: [LOG]{"key": "calories", "value": 1850}[/LOG]

- `[MEMORY]{"text": "User fact", "type": "preference"}[/MEMORY]` - Save user memory
  Types: preference, schedule, motivation, challenge, general
  Example: [MEMORY]{"text": "Prefers morning workouts", "type": "preference"}[/MEMORY]

- `[DELETE_HABIT]{"habit_id": "..."}[/DELETE_HABIT]` - Archive habit
- `[UPDATE_HABIT]{"habit_id": "...", "title": "new title"}[/UPDATE_HABIT]` - Modify habit

**BEHAVIORAL RULES**:

**Core Principles**:
- YOU HAVE ALL THE USER'S DATA ABOVE. NEVER say "I'd need to know..." - you already have it. USE IT.
- ALWAYS reference actual numbers from their data (completion rates, tracker values, streaks)
- Be PROACTIVE in suggesting habits and trackers when you see gaps
- NEVER create things without discussing first: Suggest → User agrees → Create
- When user tells you a number, LOG IT immediately using [LOG] tag
- Keep responses CONCISE (2-4 sentences max)
- Don't use markdown formatting - keep it plain text for chat bubbles
- Know when to WRAP UP: Short responses like "cool", "okay", "thanks" mean they're DONE. Respond with 1 sentence and STOP.
- Ask only ONE follow-up question at a time, not multiple

**Habit Creation Rules**:
- Check "Can add new habit" status FIRST before creating any habits
- If it says "No", DO NOT create habits. Instead explain: "You need to complete your current habits 8 times each before adding new ones"
- If it says "Yes", you can create habits BUT:
  * ALWAYS ask "Ready to create this habit?" before using [HABIT] tag
  * Only create after user confirms
  * New habits become active starting TOMORROW
  * Be SPECIFIC: "Drink 2L water daily" not "Stay hydrated"
  * Include numeric targets to enable auto-linking with trackers

**Data Logging Rules**:
- Parse numbers from natural language ("I ate 1850 calories" → [LOG]{"key": "calories", "value": 1850}[/LOG])
- Log IMMEDIATELY when user mentions a number
- Confirm after logging: "Logged 1850 calories for today"
- PROACTIVELY ask about missing data: "I see you haven't logged water today. How much have you had?"

**Memory Rules**:
- Save important facts naturally during conversation (1-2 max per chat)
- Don't announce that you're saving memories - do it silently
- Save: dietary preferences, schedule, exercise preferences, motivations, challenges
- Don't duplicate existing memories

Remember: Be conversational and natural, like a real coach texting them.
"""


async def _calculate_tracker_average(
    tracker_id: str, user_id: str, goal_id: str, days: int
) -> float | None:
    """Calculate N-day average for a tracker."""
    start_date = days_ago(days).isoformat()
    end_date = today_str()

    logs = await daily_log_service.get_logs_for_period(user_id, goal_id, start_date, end_date)

    values = []
    for log in logs:
        for entry in log.get("tracker_entries", []):
            if entry["tracker_id"] == tracker_id:
                values.append(entry["value"])

    return sum(values) / len(values) if values else None
