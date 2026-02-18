# Priya Coach AI — Master Integration Guide

> How all five prompts connect, when each fires, what data each needs,
> and how your backend orchestrates the full coaching loop.

---

## 1. The Five Prompts at a Glance

| #   | Prompt                 | File                   | Fires When                                         | Who Speaks First |
| --- | ---------------------- | ---------------------- | -------------------------------------------------- | ---------------- |
| 1   | Initial Session        | `initial_session.py`   | User creates first goal, zero conversation history | Priya            |
| 1b  | New Goal (Returning)   | `initial_session.py`   | User creates a new goal, has prior history         | Priya            |
| 2   | Coaching System Prompt | `prompt_builder.py`    | Every regular conversation turn                    | User             |
| 3   | Personalities Module   | `personalities.py`     | Injected into #1, #2, #4, #5 — not called alone    | —                |
| 4   | Review Session         | `review_session.py`    | Scheduled weekly OR data-triggered                 | Priya            |
| 5   | Proactive Check-in     | `proactive_checkin.py` | Event-triggered by backend detector                | Priya            |

---

## 2. The Decision Tree — Which Prompt Fires

```
User opens app / event detected
│
├── NEW GOAL created?
│   ├── user.conversation_count == 0
│   │   └── → PROMPT #1 (Initial Session)
│   └── user.conversation_count > 0
│       └── → PROMPT #1b (New Goal, Returning User)
│
├── PROACTIVE TRIGGER detected? (runs in background, async)
│   ├── missed_3_plus_days        → PROMPT #5 (push notification)
│   ├── habit_formed              → PROMPT #5 (message waiting)
│   └── metric_wrong_direction    → PROMPT #5 (push or waiting, based on case)
│
├── REVIEW due or triggered?
│   ├── scheduled (7 days since last review)  → PROMPT #4
│   ├── streak_broken (5+ day streak missed)  → PROMPT #4
│   ├── consistently_missing (3+ days)        → PROMPT #4
│   ├── target_at_risk (pace slipping)        → PROMPT #4
│   ├── breakthrough (habit formed)           → PROMPT #4
│   └── plateau (metric flat 10+ days)        → PROMPT #4
│
└── Regular conversation turn
    └── → PROMPT #2 (Coaching System Prompt Builder)
```

> **Priority order when multiple triggers fire simultaneously:**
> Proactive check-in > Review session > Regular conversation.
> Never fire more than one prompt type per session open.

---

## 3. Prompt #1 — Initial Session

### When It Fires

```python
if user.total_goals == 1 and user.conversation_count == 0:
    use_prompt = "initial_session"
```

### Data Required (pre-compute before calling model)

```python
{
    "title":                str,   # goal title
    "description":          str,   # goal description
    "primary_metric_name":  str,   # e.g. "Weight"
    "primary_metric_unit":  str,   # e.g. "kg"
    "initial_value":        float, # e.g. 92.0
    "target_value":         float, # e.g. 80.0
    "target_date":          str,   # ISO date string
    "gap":                  float, # target_value - initial_value (pre-computed)
    "days_remaining":       int,   # days until target_date (pre-computed)
    "coaching_style_fragment": str, # from personalities.get_personality_prompt(user.coaching_style)
    "questionnaire_context":   str, # formatted Q&A from onboarding
    "conversation_history":    str, # empty on first call, populated on subsequent turns
    "current_phase":           str, # "exploring" | "proposing" | "creating" | "complete"
}
```

### Response Shape

```json
{
  "phase": "exploring | proposing | creating | complete",
  "message": "Priya's message with action tags embedded"
}
```

### Backend Responsibilities

```python
# 1. Parse phase from response — store on session
session.current_phase = response["phase"]

# 2. Strip action tags before showing message to user
visible_message = strip_action_tags(response["message"])

# 3. Execute action tags
execute_tags(response["message"], user_id, goal_id)

# 4. On phase == "complete" — mark initial session done
if response["phase"] == "complete":
    user.initial_session_complete = True
    user.conversation_count += 1

# 5. Store conversation turn
conversation_history.append({
    "role": "assistant",
    "content": visible_message
})
```

### Phase State Machine

```
exploring → proposing → creating → complete
              ↑              |
              └──────────────┘  (if user pushes back, return to proposing)
```

---

## 4. Prompt #2 — Coaching System Prompt Builder

### When It Fires

Every regular conversation turn where no other prompt takes priority.

```python
if not (new_goal or review_due or proactive_triggered):
    system_prompt = await build_coaching_system_prompt(...)
```

### Data Required

```python
# Passed to build_coaching_system_prompt()
user              = user_document          # includes memories, coaching_style
goal              = active_goal_document   # includes ai_context, primary_tracker
habits            = active_habits_list     # includes streaks, formation_count, completion data
trackers          = active_trackers_list   # includes unit, direction, target_value
today_logs        = today_daily_log        # includes tracker_entries logged today
upcoming_checkins = next_3_checkins        # scheduled check-in dates
```

### What the Builder Pre-Computes

```python
# These are computed inside the builder — backend doesn't need to pre-compute
_tracker_average(tracker_id, user_id, goal_id, days=7)   # 7-day avg
_tracker_average(tracker_id, user_id, goal_id, days=14)  # 14-day avg
_interpret_trend(avg_7, avg_14, target, direction)        # plain-English trend
_build_coaches_eye(habits, trackers)                      # what deserves attention
```

### Response Shape

```json
{
  "message": "Priya's response with any action tags embedded"
}
```

### Backend Responsibilities

```python
# 1. Detect conversation type from user message (logging vs coaching vs casual)
#    — handled by Priya, but backend can pre-classify for analytics

# 2. Strip tags, execute tags, store turn
visible_message = strip_action_tags(response["message"])
execute_tags(response["message"], user_id, goal_id)
conversation_history.append({"role": "assistant", "content": visible_message})

# 3. Increment conversation count
user.conversation_count += 1
```

---

## 5. Prompt #3 — Personalities Module

### This Is Not Called Directly

It is injected into every other prompt via:

```python
from app.prompts.personalities import get_personality_prompt

coaching_style_fragment = get_personality_prompt(user.coaching_style)
# Inject into: initial_session, coaching_system_prompt, review_session, proactive_checkin
```

### Injection Order Inside Each Prompt

```
1. MOOD_DETECTION_PROMPT     ← read the room first
2. PERSONALITY FRAGMENT      ← base style
3. ADAPTATION_RULES          ← how to bend based on mood
```

### Context Flag Detection (for metric triggers)

```python
from app.prompts.personalities import detect_metric_context_flag

context_flag = detect_metric_context_flag(user.memories)
# Returns: "creatine" | "new_gym" | "illness" | "hormonal" | "none"
# Used in Prompt #5 to determine Case A vs Case B response
```

### Updating Coaching Style

```python
# User can change their coaching style anytime
# Just update user.coaching_style — next session picks it up automatically
user.coaching_style = "strict"  # strict | balanced | supportive | scientific
```

---

## 6. Prompt #4 — Review Session

### When It Fires

**Scheduled:**

```python
days_since_last_review = (today - user.last_review_date).days
if days_since_last_review >= 7:
    trigger_review(trigger_type="scheduled")
```

**Data-triggered (check daily, async):**

```python
def detect_review_triggers(user, habits, trackers):
    for habit in habits:
        streak_before = habit.streak_before_last_miss
        if habit.consecutive_missed >= 1 and streak_before >= 5:
            return "streak_broken"

    for habit in habits:
        if habit.consecutive_missed >= 3:
            return "consistently_missing"

    if goal_pace_ratio < 0.75:
        return "target_at_risk"

    for habit in habits:
        if habit.just_formed:  # formation_count just hit 8
            return "breakthrough"

    for tracker in trackers:
        if tracker.days_since_movement >= 10:
            return "plateau"

    return None
```

### Data Required

```python
{
    "trigger_type":         str,   # scheduled | streak_broken | consistently_missing | etc.
    "trigger_reason":       str,   # human-readable explanation
    "coaching_style_fragment": str,
    "memories_section":     str,   # from _build_memories_section()
    "goal_title":           str,
    "goal_description":     str,
    "current_phase":        str,   # goal phase (building_foundation, etc.)
    "target_date":          str,
    "days_remaining":       int,
    "primary_metric_name":  str,
    "current_value":        float,
    "target_value":         float,
    "primary_metric_unit":  str,
    "timeline_health":      str,   # from build_timeline_health()
    "pace_note":            str,   # from build_timeline_health()
    "habits_summary":       str,   # from build_habits_summary_for_review()
    "tracker_summary":      str,   # from build_tracker_summary_for_review()
    "conversation_history": str,   # grows as review conversation continues
    "task_instruction":     str,   # from get_review_task_instruction(stage)
}
```

### Review Conversation Stages

Backend tracks which stage the review is in and injects the right task instruction:

```python
# Stage lifecycle
review_stages = ["opening", "mid_conversation", "proposing_change", "closing"]

# Start at opening
session.review_stage = "opening"

# After first user reply → mid_conversation
session.review_stage = "mid_conversation"

# When Priya proposes a change → proposing_change
# Detect: response message contains [HABIT] or [UPDATE_HABIT] proposal language
# but NO actual tags yet (those come after confirmation)

# When user confirms and tags are created → closing
session.review_stage = "closing"

# After closing message → review complete
user.last_review_date = today
```

### Response Shape

```json
{
  "review_type": "scheduled | streak_broken | ...",
  "message": "Priya's message with any action tags embedded"
}
```

---

## 7. Prompt #5 — Proactive Check-in

### When It Fires

Runs as a background job, separate from user session:

```python
# Run once daily, async — check all active users
async def proactive_check_daily():
    for user in active_users:
        trigger = detect_proactive_trigger(user)
        if trigger:
            message = await generate_proactive_message(user, trigger)
            deliver_proactive_message(user, message)
```

### Trigger Detection

```python
def detect_proactive_trigger(user, habits, trackers, goal):

    # Priority 1: Missed days (most urgent)
    for habit in habits:
        if habit.consecutive_missed >= 3:
            return {
                "type": "missed_3_plus_days",
                "habit": habit
            }

    # Priority 2: Metric moving wrong direction
    primary = goal.primary_tracker
    if is_moving_wrong_direction(primary, days=7):
        context_flag = detect_metric_context_flag(user.memories)
        return {
            "type": "metric_wrong_direction",
            "metric": primary,
            "context_flag": context_flag
        }

    # Priority 3: Habit just formed
    for habit in habits:
        if habit.just_formed and not habit.formation_celebrated:
            return {
                "type": "habit_formed",
                "habit": habit
            }

    return None
```

### Delivery Routing

```python
def deliver_proactive_message(user, response):
    delivery = response["delivery"]

    if delivery == "push_notification":
        # Send push notification — opens directly into chat
        push_service.send(
            user_id=user.id,
            title="Priya",
            body=response["message"][:80],  # preview truncates at ~80 chars
            action="open_chat"
        )

    elif delivery == "message_waiting":
        # Store as pending message — shown when user opens app
        pending_messages.create(
            user_id=user.id,
            message=response["message"],
            trigger_type=response["trigger_type"]
        )
```

### Response Shape

```json
{
  "trigger_type": "missed_3_plus_days | habit_formed | metric_wrong_direction",
  "metric_case": "expected | unexpected | n/a",
  "delivery": "push_notification | message_waiting",
  "message": "Priya's proactive message — no action tags"
}
```

### After User Replies to Proactive Message

```python
# Proactive check-in has started a conversation
# Hand off to Prompt #2 (regular coaching) for all subsequent turns
# Pass the proactive message as the first assistant turn in conversation_history

conversation_history = [
    {"role": "assistant", "content": proactive_message}
]
# Then continue with build_coaching_system_prompt() for all user replies
```

---

## 8. Action Tag Execution

All prompts embed action tags in the message. Backend strips them before display and executes them. Here is the full tag reference and execution map:

```python
import re, json

TAG_PATTERN = re.compile(r'\[(\w+)\](.*?)\[/\1\]', re.DOTALL)

def execute_tags(message: str, user_id: str, goal_id: str):
    for match in TAG_PATTERN.finditer(message):
        tag  = match.group(1)
        body = match.group(2).strip()

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            log_error(f"Invalid JSON in tag [{tag}]: {body}")
            continue

        if tag == "TRACKER":
            tracker_id = tracker_service.create(user_id, goal_id, data)
            # Store tracker_id so subsequent HABIT tags can reference it
            session.last_created_tracker_id = tracker_id

        elif tag == "HABIT":
            # Replace placeholder if model used {{tracker_id}}
            if data.get("linked_tracker_id") == "{{tracker_id}}":
                data["linked_tracker_id"] = session.last_created_tracker_id
            habit_service.create(user_id, goal_id, data)

        elif tag == "UPDATE_HABIT":
            habit_service.update(user_id, data["habit_id"], data)

        elif tag == "DELETE_HABIT":
            habit_service.archive(user_id, data["habit_id"])

        elif tag == "LOG":
            log_service.log_tracker_value(user_id, goal_id, data["key"], data["value"])

        elif tag == "MEMORY":
            memory_service.save(user_id, {
                "text": data["text"],
                "type": data.get("type", "general"),
                "timestamp": now_iso()
            })


def strip_action_tags(message: str) -> str:
    return TAG_PATTERN.sub('', message).strip()
```

---

## 9. Memory System

### When Memories Are Saved

- **Initial Session** — 3-5 memories seeded from questionnaire (silently)
- **Every regular session** — 1-2 new facts Priya learns (silently)
- **Review Session** — new patterns or context discovered during review

### Memory Priority (used in `_build_memories_section`)

```
challenge    → highest priority (failure patterns, blockers)
motivation   → high priority (what actually drives them)
schedule     → medium priority (affects habit design)
preference   → medium priority (affects habit design)
general      → lower priority
```

### Memory Deduplication

```python
def save_memory(user_id, new_memory):
    existing = memory_service.get_all(user_id)

    # Simple similarity check — avoid exact duplicates
    for mem in existing:
        if similarity_score(mem["text"], new_memory["text"]) > 0.85:
            return  # Skip duplicate

    memory_service.insert(user_id, new_memory)
```

### Memory Pruning

```python
# Cap at 50 total memories
# When over limit: drop oldest "general" type first, then oldest of each type
def prune_memories(user_id):
    memories = memory_service.get_all(user_id)
    if len(memories) <= 50:
        return

    priority_order = ["general", "preference", "schedule", "motivation", "challenge"]
    for mem_type in priority_order:
        candidates = [m for m in memories if m["type"] == mem_type]
        if candidates:
            memory_service.delete(candidates[0]["id"])
            return
```

---

## 10. Formation Gate

The formation gate is the most important rule in the habit system.
It is enforced at THREE levels:

```
Level 1 — Prompt text
  Every prompt explicitly states the rule:
  "Can add new habit: NO — active habits need 8 completions each first"

Level 2 — Model instruction
  _build_habits_section() outputs "Can add new habit: YES/NO"
  Priya reads this and respects it

Level 3 — Backend enforcement (safety net)
  Before executing any [HABIT] tag:
```

```python
def execute_habit_tag(user_id, goal_id, data):
    active_habits = habit_service.get_active(user_id, goal_id)
    all_formed = all(h["is_formed"] for h in active_habits)

    if not all_formed:
        log_warning(f"Habit creation blocked — formation gate not cleared")
        return  # Do not create the habit

    habit_service.create(user_id, goal_id, data)
```

---

## 11. Session State Summary

Track these fields per user session to orchestrate correctly:

```python
class SessionState:
    # Initial session
    initial_session_phase: str        # exploring | proposing | creating | complete
    initial_session_complete: bool

    # Review session
    review_active: bool
    review_stage: str                 # opening | mid_conversation | proposing_change | closing
    review_trigger_type: str

    # Proactive
    pending_proactive_message: str    # stored until user opens app
    last_proactive_trigger: str       # avoid same trigger twice in a row

    # General
    conversation_count: int
    last_created_tracker_id: str      # for linking HABIT to most recently created TRACKER
    last_review_date: date
    coaching_style: str               # strict | balanced | supportive | scientific
```

---

## 12. Quick Reference — Data Checklist Per Prompt

| Data Field                          | #1 Initial | #2 Coaching    | #4 Review | #5 Proactive |
| ----------------------------------- | ---------- | -------------- | --------- | ------------ |
| `coaching_style_fragment`           | ✓          | ✓ (in builder) | ✓         | ✓            |
| `questionnaire_context`             | ✓          | —              | —         | —            |
| `conversation_history`              | ✓          | ✓              | ✓         | —            |
| `current_phase` (session)           | ✓          | —              | —         | —            |
| `memories_section`                  | —          | ✓ (in builder) | ✓         | ✓            |
| `habits_summary`                    | —          | ✓ (in builder) | ✓         | ✓            |
| `tracker_summary`                   | —          | ✓ (in builder) | ✓         | ✓            |
| `today_logs`                        | —          | ✓              | —         | —            |
| `upcoming_checkins`                 | —          | ✓              | —         | —            |
| `trigger_type`                      | —          | —              | ✓         | ✓            |
| `review_stage` + `task_instruction` | —          | —              | ✓         | —            |
| `timeline_health` + `pace_note`     | —          | —              | ✓         | —            |
| `context_flag` (metric)             | —          | —              | —         | ✓            |
| `previous_proactive_messages`       | —          | —              | —         | ✓            |
| `gap` + `days_remaining`            | ✓          | —              | —         | —            |
