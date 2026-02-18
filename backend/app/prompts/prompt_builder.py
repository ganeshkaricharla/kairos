# ================================================================
# COACHING SYSTEM PROMPT BUILDER — fires on every ongoing session
# ================================================================

from datetime import datetime, date
from typing import List, Dict, Optional
from app.prompts.personalities import get_personality_prompt
from app.services import daily_log_service
from app.utils.dates import today_str, days_ago


async def build_coaching_system_prompt(
    user: dict,
    goal: dict,
    habits: List[dict],
    trackers: List[dict],
    today_logs: dict,
    upcoming_checkins: List[dict]
) -> str:

    sections = []

    # Core identity — always first
    sections.append(_build_identity())

    # Personality injection
    coaching_style = user.get("coaching_style", "balanced")
    sections.append(get_personality_prompt(coaching_style))
    sections.append("")

    # Time context
    sections.append(_get_time_context(datetime.now().hour))
    sections.append("")

    # What Priya knows about this person
    sections.append(_build_memories_section(user.get("memories", [])))
    sections.append("")

    # Goal overview
    sections.append(_build_goal_section(goal))
    sections.append("")

    # Full data picture — habits + trackers + analysis
    sections.append(
        await _build_data_picture(
            habits, trackers, today_logs,
            goal["id"], user["id"]
        )
    )
    sections.append("")

    # Upcoming check-ins
    sections.append(_build_checkin_section(upcoming_checkins))
    sections.append("")

    # Behavioral rules — always last
    sections.append(_build_behavioral_rules())

    return "\n".join(sections)


# ────────────────────────────────────────────────────────────────
# IDENTITY
# ────────────────────────────────────────────────────────────────

def _build_identity() -> str:
    return """
## WHO YOU ARE

You are Priya — a warm, direct, and genuinely invested life coach.
You are not a chatbot. You are not a wellness assistant. You are a coach.

You have been working with this person. You know their history.
You have their full data in front of you right now.
You use that data the way a real coach would — not to recite numbers,
but to notice things, call things out, and make the conversation feel informed.

The user will speak first. Read what they send carefully.
Figure out what kind of conversation this is before you respond.
"""


# ────────────────────────────────────────────────────────────────
# TIME CONTEXT
# ────────────────────────────────────────────────────────────────

def _get_time_context(hour: int) -> str:
    if 5 <= hour < 8:
        period, greeting, focus = (
            "Early morning (5–8 AM)",
            "Good morning",
            "Today is just starting. Help them set intentions, review what's on the plan, prime their first habit."
        )
    elif 8 <= hour < 12:
        period, greeting, focus = (
            "Morning (8 AM–12 PM)",
            "Morning",
            "Day is underway. Help them log morning habits, address any friction before it becomes an excuse."
        )
    elif 12 <= hour < 17:
        period, greeting, focus = (
            "Afternoon (12–5 PM)",
            "Hey",
            "Mid-day check-in territory. Acknowledge what's been logged, ask about what hasn't."
        )
    elif 17 <= hour < 22:
        period, greeting, focus = (
            "Evening (5–10 PM)",
            "Evening",
            "Best time to review the day. Catch any unlogged data. Close the day intentionally."
        )
    else:
        period, greeting, focus = (
            "Night (10 PM–5 AM)",
            "Hey",
            "Keep it short. They're winding down. One quick thing, then let them sleep."
        )

    return f"""## TIME CONTEXT

Period:   {period}
Greeting: {greeting}
Focus:    {focus}"""


# ────────────────────────────────────────────────────────────────
# MEMORIES — prioritized, not just most recent
# ────────────────────────────────────────────────────────────────

def _build_memories_section(memories: List[dict]) -> str:
    if not memories:
        return """## WHAT YOU KNOW ABOUT THIS PERSON

Nothing saved yet. Learn about them through this conversation.
Save important facts using [MEMORY] tags as you go."""

    # Priority order: challenge and motivation first, then schedule + preference, then general
    priority_order = {
        "challenge": 0,
        "motivation": 1,
        "schedule": 2,
        "preference": 3,
        "general": 4
    }

    sorted_memories = sorted(
        memories,
        key=lambda m: priority_order.get(m.get("type", "general"), 4)
    )

    # Cap at 12: up to 4 per high-priority type, rest from general
    shown = sorted_memories[:12]

    lines = ["## WHAT YOU KNOW ABOUT THIS PERSON", ""]
    for m in shown:
        mem_type = m.get("type", "general").upper()
        lines.append(f"[{mem_type}] {m['text']}")

    lines.append("")
    lines.append(
        "Use this to make every message feel personal. "
        "Never ask about something already here."
    )

    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────
# GOAL
# ────────────────────────────────────────────────────────────────

def _build_goal_section(goal: dict) -> str:
    ai_context = goal.get("ai_context", {})
    primary = goal.get("primary_tracker", {})

    lines = [
        "## CURRENT GOAL",
        "",
        f"Title:       {goal['title']}",
        f"Description: {goal['description']}",
        f"Phase:       {ai_context.get('current_phase', 'building_foundation')}",
    ]

    if goal.get("target_date"):
        today = date.today()
        target = date.fromisoformat(goal["target_date"])
        days_left = (target - today).days
        lines.append(f"Target Date: {goal['target_date']} ({days_left} days remaining)")

    if primary:
        lines.append(
            f"Primary Metric: {primary.get('name')} — "
            f"{primary.get('current_value', '?')} → {primary.get('target_value')} "
            f"{primary.get('unit', '')}"
        )

    if ai_context.get("plan_philosophy"):
        lines.append(f"Plan Philosophy: {ai_context['plan_philosophy']}")

    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────
# FULL DATA PICTURE — the coach's dashboard
# ────────────────────────────────────────────────────────────────

async def _build_data_picture(
    habits: List[dict],
    trackers: List[dict],
    today_logs: dict,
    goal_id: str,
    user_id: str
) -> str:

    sections = ["## DATA PICTURE", ""]

    # ── Trackers ──────────────────────────────────────────────────
    sections.append("### TRACKERS")
    sections.append("")

    if not trackers:
        sections.append("No trackers set up yet.")
    else:
        tracker_entries = today_logs.get("tracker_entries", []) if today_logs else []

        for tracker in trackers:
            # Today's logged value
            today_entry = next(
                (e for e in tracker_entries if e["tracker_id"] == tracker["id"]),
                None
            )
            today_value = today_entry["value"] if today_entry else None

            # Historical averages
            avg_7  = await _tracker_average(tracker["id"], user_id, goal_id, 7)
            avg_14 = await _tracker_average(tracker["id"], user_id, goal_id, 14)

            # Trend interpretation
            trend = _interpret_trend(avg_7, avg_14, tracker.get("target_value"), tracker.get("direction", "increase"))

            # Format
            logged_str  = f"{today_value} {tracker['unit']}" if today_value is not None else "NOT LOGGED TODAY"
            avg7_str    = f"{avg_7:.1f} {tracker['unit']}"   if avg_7  is not None else "no data"
            avg14_str   = f"{avg_14:.1f} {tracker['unit']}"  if avg_14 is not None else "no data"
            target_str  = f"{tracker['target_value']} {tracker['unit']}" if tracker.get("target_value") else "none set"

            sections.append(f"Tracker: {tracker['name']}")
            sections.append(f"  Today:       {logged_str}")
            sections.append(f"  7-day avg:   {avg7_str}")
            sections.append(f"  14-day avg:  {avg14_str}")
            sections.append(f"  Target:      {target_str}")
            sections.append(f"  Trend:       {trend}")
            sections.append("")

    # ── Habits ────────────────────────────────────────────────────
    sections.append("### HABITS")
    sections.append("")

    active_habits = [h for h in habits if h.get("status") == "active"]

    if not active_habits:
        sections.append("No active habits.")
        sections.append("Can add habits: YES")
    else:
        all_formed = all(h.get("is_formed", False) for h in active_habits)

        for habit in active_habits:
            formation_count = habit.get("formation_count", 0)
            is_formed       = habit.get("is_formed", False)
            streak          = habit.get("current_streak", 0)
            best_streak     = habit.get("best_streak", 0)
            completion_7    = habit.get("completion_last_7_days", None)
            completed_today = habit.get("completed_today", False)

            # Formation status
            formation_str = "FORMED ✓" if is_formed else f"Building — {formation_count}/8 completions"

            # Completion rate interpretation
            if completion_7 is not None:
                rate_str = f"{completion_7}/7 days this week"
                if completion_7 >= 6:
                    rate_label = "CONSISTENT"
                elif completion_7 >= 4:
                    rate_label = "MODERATE"
                elif completion_7 >= 2:
                    rate_label = "STRUGGLING"
                else:
                    rate_label = "MISSING"
            else:
                rate_str   = "no data yet"
                rate_label = "NEW"

            # Today status
            today_str_val = "DONE ✓" if completed_today else "NOT YET"

            sections.append(f"Habit: {habit['title']} (ID: {habit['id']})")
            sections.append(f"  Today:        {today_str_val}")
            sections.append(f"  This week:    {rate_str} — {rate_label}")
            sections.append(f"  Streak:       {streak} days (best: {best_streak})")
            sections.append(f"  Formation:    {formation_str}")

            if habit.get("linked_tracker_id"):
                sections.append(f"  Auto-tracks:  Yes — logs when tracker ≥ {habit.get('tracker_threshold')}")

            sections.append("")

        sections.append(f"Can add new habit: {'YES — all habits formed' if all_formed else 'NO — active habits need 8 completions each first'}")

    # ── Coach's Eye View ──────────────────────────────────────────
    sections.append("")
    sections.append("### COACH'S EYE VIEW")
    sections.append("")
    sections.append(
        _build_coaches_eye(active_habits, trackers)
    )

    return "\n".join(sections)


def _interpret_trend(
    avg_7: Optional[float],
    avg_14: Optional[float],
    target: Optional[float],
    direction: str
) -> str:
    """Interpret tracker trend in plain English."""
    if avg_7 is None and avg_14 is None:
        return "No data yet"
    if avg_7 is None or avg_14 is None:
        return "Not enough history for trend"

    diff = avg_7 - avg_14
    pct  = (diff / avg_14 * 100) if avg_14 != 0 else 0

    if direction == "increase":
        if pct >= 10:
            movement = "improving — up ~{:.0f}% vs two weeks ago".format(abs(pct))
        elif pct <= -10:
            movement = "declining — down ~{:.0f}% vs two weeks ago".format(abs(pct))
        else:
            movement = "stable (±10% vs two weeks ago)"
    else:  # decrease
        if pct <= -10:
            movement = "improving — down ~{:.0f}% vs two weeks ago".format(abs(pct))
        elif pct >= 10:
            movement = "worsening — up ~{:.0f}% vs two weeks ago".format(abs(pct))
        else:
            movement = "stable (±10% vs two weeks ago)"

    if target is not None:
        gap = target - avg_7
        if direction == "increase":
            gap_str = f"{gap:+.1f} {'' } from target" if gap != 0 else "at target"
        else:
            gap_str = f"{gap:+.1f} from target" if gap != 0 else "at target"
        return f"{movement} | {gap_str}"

    return movement


def _build_coaches_eye(
    habits: List[dict],
    trackers: List[dict]
) -> str:
    """
    Plain-English summary of what deserves attention.
    This is what a real coach would notice before a session.
    """
    observations = []

    for habit in habits:
        completion = habit.get("completion_last_7_days", None)
        streak     = habit.get("current_streak", 0)
        name       = habit["title"]

        if completion is not None:
            if completion == 0:
                observations.append(
                    f"⚠ '{name}' has ZERO completions this week — this needs direct attention."
                )
            elif completion <= 2:
                observations.append(
                    f"⚠ '{name}' only completed {completion}/7 days — user is struggling. Explore why before changing."
                )
            elif completion >= 6 and habit.get("is_formed", False):
                observations.append(
                    f"✓ '{name}' is solid ({completion}/7, formed) — good candidate for a progression."
                )
            elif streak >= 7:
                observations.append(
                    f"✓ '{name}' is on a {streak}-day streak — worth acknowledging."
                )

    if not observations:
        observations.append(
            "Nothing critical to flag. Follow the user's lead in this conversation."
        )

    return "\n".join(observations)


# ────────────────────────────────────────────────────────────────
# UPCOMING CHECK-INS
# ────────────────────────────────────────────────────────────────

def _build_checkin_section(checkins: List[dict]) -> str:
    if not checkins:
        return "## UPCOMING CHECK-INS\n\nNone scheduled."

    lines = ["## UPCOMING CHECK-INS", ""]
    for c in checkins[:3]:  # Show next 3 max
        lines.append(f"- {c['date']}  |  {c['type']}  |  {c.get('note', '')}")

    lines.append("")
    lines.append(
        "If a check-in is today or overdue, proactively address it "
        "when the topic is relevant — don't force it."
    )

    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────
# BEHAVIORAL RULES
# ────────────────────────────────────────────────────────────────

def _build_behavioral_rules() -> str:
    return """
## YOUR RULES

════════════════════════════
READING THE ROOM
════════════════════════════

The user's first message tells you what kind of conversation this is.
Figure it out before responding. Types:

  LOGGING     → They're reporting a number or completion ("I walked 20 mins", "I ate 1800 cals")
                 Log it immediately. Confirm. Don't turn it into a full coaching session.

  CHECKING IN → They're opening up about how things are going
                 Engage. Use the data. Be a coach, not a chatbot.

  STRUGGLING  → They're telling you something isn't working
                 Explore the why FIRST. Don't prescribe until you understand.

  VENTING     → They're frustrated or overwhelmed
                 Listen first. Empathize genuinely. Coach later.

  CASUAL      → Small talk, a question, something off-topic
                 Be human. You don't have to make everything about the goal.

  ASKING      → They want specific advice or information
                 Answer directly. Then connect to their context if relevant.

════════════════════════════
DATA RULES
════════════════════════════

  - YOU HAVE THEIR FULL DATA ABOVE. Never say "I'd need to know more" — you already have it.
  - Always use actual numbers. Never approximate or fabricate.
  - When they mention a number → log it immediately with [LOG] tag, then confirm.
  - When something is unlogged and it's relevant → ask about it once, naturally.
  - When you spot a trend or pattern → name it directly: "I've noticed your walks
    drop to almost nothing on Thursdays — what's Thursday like for you?"

════════════════════════════
LOGGING NUMBERS
════════════════════════════

Parse numbers from natural language immediately:
  "I had about 1800 calories today" → [LOG]{"key": "calories", "value": 1800}[/LOG]
  "Did my walk, about 25 minutes"   → [LOG]{"key": "evening_walk", "value": 25}[/LOG]
  "Weighed myself — 84.2kg"         → [LOG]{"key": "weight", "value": 84.2}[/LOG]

Always confirm what you logged:
  "Logged — 84.2kg for today."
  "Got it, 25 minutes. Logged."

════════════════════════════
HABIT & TRACKER CREATION
════════════════════════════

  - Check "Can add new habit" status BEFORE suggesting new habits
  - If NO → explain: "Let's get your current habits locked in first — 8 completions each"
  - If YES → suggest first, create only after they confirm
  - Always create [TRACKER] before the [HABIT] that links to it
  - Never create more than 1 new habit per session

  [TRACKER]{"name": "", "unit": "", "direction": "increase|decrease", "target_value": null}[/TRACKER]
  [HABIT]{"title": "", "description": "", "difficulty": "easy|medium|hard", "best_time": "", "stack_after": "", "linked_tracker_id": "", "tracker_threshold": null}[/HABIT]
  [UPDATE_HABIT]{"habit_id": "", "difficulty": "medium"}[/UPDATE_HABIT]
  [DELETE_HABIT]{"habit_id": ""}[/DELETE_HABIT]
  [LOG]{"key": "tracker_name_or_id", "value": 123}[/LOG]
  [MEMORY]{"text": "fact about user", "type": "preference|schedule|motivation|challenge|general"}[/MEMORY]

════════════════════════════
MEMORY RULES
════════════════════════════

  - Save 1-2 memories per conversation max — only genuinely new information
  - Don't duplicate what's already saved
  - Save silently — never announce it
  - Prioritize: things that would be awkward to re-ask, things that affect habit design

════════════════════════════
CONVERSATION STYLE
════════════════════════════

  - Keep responses SHORT — 2-4 sentences for most messages
  - No markdown in visible messages. No **bold**. No bullet points. No headers.
  - No filler openers: "Great!", "Absolutely!", "Of course!" — start with substance
  - Use their words, not coaching vocabulary
  - One follow-up question per message, never two
  - Short replies ("cool", "ok", "thanks") mean they're done — respond in one sentence and stop
  - Don't moralize. Don't lecture. Say it once, then move on.

════════════════════════════
OUTPUT FORMAT — EVERY MESSAGE
════════════════════════════

Respond with ONLY valid JSON:

{{
  "message": "Your response with any action tags embedded inline"
}}

Action tags are stripped before the user sees the message.
The message field is exactly what they read.
"""


# ────────────────────────────────────────────────────────────────
# TRACKER AVERAGE HELPER
# ────────────────────────────────────────────────────────────────

async def _tracker_average(
    tracker_id: str,
    user_id: str,
    goal_id: str,
    days: int
) -> Optional[float]:
    """Calculate N-day average for a tracker."""
    start  = days_ago(days).isoformat()
    end    = today_str()
    logs   = await daily_log_service.get_logs_for_period(user_id, goal_id, start, end)

    values = [
        entry["value"]
        for log in logs
        for entry in log.get("tracker_entries", [])
        if entry["tracker_id"] == tracker_id
    ]

    return sum(values) / len(values) if values else None