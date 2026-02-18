"""
AI Tools - Functions the AI can call to retrieve data on-demand.

Instead of dumping all data into the prompt, the AI can request specific data
using these tools. This saves tokens and makes the system more efficient.
"""

import json
from typing import Any

from app.services import habit_service, tracker_service, daily_log_service, goal_service
from app.utils.dates import days_ago, date_range


# Tool definitions in OpenAI function calling format
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_active_habits",
            "description": "Get all active habits for a goal. Use this when you need to see what habits the user is currently working on.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID to get habits for",
                    }
                },
                "required": ["goal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_trackers",
            "description": "Get all trackers (metrics) for a goal. Use this when you need to see what metrics the user is tracking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID to get trackers for",
                    }
                },
                "required": ["goal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_logs",
            "description": "Get daily logs (habit completions and tracker values) for a date range. Use this when you need to see the user's tracking history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The user ID",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back (default: 7)",
                        "default": 7,
                    }
                },
                "required": ["goal_id", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_goal_details",
            "description": "Get detailed information about a goal including title, description, target values, and questionnaire responses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID",
                    }
                },
                "required": ["goal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_habit_performance",
            "description": "Get performance statistics for a specific habit over a date range. Shows completion counts, streaks, and rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "habit_id": {
                        "type": "string",
                        "description": "The habit ID",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The user ID",
                    },
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default: 7)",
                        "default": 7,
                    }
                },
                "required": ["habit_id", "user_id", "goal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tracker_trend",
            "description": "Get trend data for a specific tracker over a date range. Shows values and trend direction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracker_id": {
                        "type": "string",
                        "description": "The tracker ID",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The user ID",
                    },
                    "goal_id": {
                        "type": "string",
                        "description": "The goal ID",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default: 7)",
                        "default": 7,
                    }
                },
                "required": ["tracker_id", "user_id", "goal_id"],
            },
        },
    },
]


async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool and return the result as a JSON string."""
    try:
        if tool_name == "get_active_habits":
            habits = await habit_service.list_habits(
                arguments["goal_id"], status="active"
            )
            print(f"[TOOL DEBUG] get_active_habits called for goal {arguments['goal_id']}")
            print(f"[TOOL DEBUG] Found {len(habits)} habits: {[h.get('title') for h in habits]}")
            return json.dumps({
                "habits": [
                    {
                        "id": h["id"],
                        "title": h["title"],
                        "description": h.get("description", ""),
                        "difficulty": h.get("difficulty", "easy"),
                        "frequency": h.get("frequency", "daily"),
                        "activated_at": h.get("activated_at").isoformat() if h.get("activated_at") else None,
                        "linked_tracker_id": h.get("linked_tracker_id"),
                        "tracker_threshold": h.get("tracker_threshold"),
                    }
                    for h in habits
                ]
            })

        elif tool_name == "get_trackers":
            trackers = await tracker_service.list_trackers(arguments["goal_id"])
            return json.dumps({
                "trackers": [
                    {
                        "id": t["id"],
                        "name": t["name"],
                        "unit": t.get("unit", ""),
                        "direction": t.get("direction", "increase"),
                        "target_value": t.get("target_value"),
                        "is_primary": t.get("is_primary", False),
                    }
                    for t in trackers
                ]
            })

        elif tool_name == "get_daily_logs":
            days = arguments.get("days", 7)
            start_date = days_ago(days)
            end_date = days_ago(0)
            start = start_date.isoformat()
            end = end_date.isoformat()

            logs = await daily_log_service.get_logs_for_period(
                arguments["user_id"],
                arguments["goal_id"],
                start,
                end
            )

            return json.dumps({
                "logs": [
                    {
                        "date": log["date"],
                        "habit_completions": log.get("habit_completions", []),
                        "tracker_entries": log.get("tracker_entries", []),
                    }
                    for log in logs
                ]
            })

        elif tool_name == "get_goal_details":
            goal = await goal_service.get_goal(arguments["goal_id"])
            return json.dumps({
                "title": goal["title"],
                "description": goal.get("description", ""),
                "primary_metric_name": goal.get("primary_metric_name", ""),
                "primary_metric_unit": goal.get("primary_metric_unit", ""),
                "initial_value": goal.get("initial_value"),
                "target_value": goal.get("target_value"),
                "target_date": goal.get("target_date"),
                "questionnaire_responses": goal.get("questionnaire_responses", {}),
                "ai_context": goal.get("ai_context", {}),
            })

        elif tool_name == "get_habit_performance":
            habit = await habit_service.get_habit(arguments["habit_id"])
            if not habit:
                return json.dumps({"error": "Habit not found"})

            days = arguments.get("days", 7)
            start_date = days_ago(days)
            end_date = days_ago(0)
            start = start_date.isoformat()
            end = end_date.isoformat()

            logs = await daily_log_service.get_logs_for_period(
                arguments["user_id"],
                arguments["goal_id"],
                start,
                end
            )

            dates = date_range(start_date, end_date)
            completions = []
            for log in logs:
                for completion in log.get("habit_completions", []):
                    if completion["habit_id"] == arguments["habit_id"]:
                        completions.append({
                            "date": log["date"],
                            "completed": completion["completed"]
                        })

            completed_count = sum(1 for c in completions if c["completed"])
            total_days = len(dates)
            rate = completed_count / total_days if total_days > 0 else 0

            return json.dumps({
                "habit_title": habit["title"],
                "completed_count": completed_count,
                "total_days": total_days,
                "completion_rate": round(rate, 2),
                "completions": completions,
            })

        elif tool_name == "get_tracker_trend":
            tracker = await tracker_service.get_tracker(arguments["tracker_id"])
            if not tracker:
                return json.dumps({"error": "Tracker not found"})

            days = arguments.get("days", 7)
            start_date = days_ago(days)
            end_date = days_ago(0)
            start = start_date.isoformat()
            end = end_date.isoformat()

            logs = await daily_log_service.get_logs_for_period(
                arguments["user_id"],
                arguments["goal_id"],
                start,
                end
            )

            dates = date_range(start_date, end_date)
            values = []
            for d in dates:
                for log in logs:
                    if log["date"] == d:
                        for entry in log.get("tracker_entries", []):
                            if entry["tracker_id"] == arguments["tracker_id"]:
                                values.append({
                                    "date": d,
                                    "value": entry["value"]
                                })

            trend = "stable"
            if len(values) >= 2:
                if values[-1]["value"] > values[0]["value"]:
                    trend = "increasing"
                elif values[-1]["value"] < values[0]["value"]:
                    trend = "decreasing"

            return json.dumps({
                "tracker_name": tracker["name"],
                "unit": tracker.get("unit", ""),
                "values": values,
                "trend": trend,
                "latest_value": values[-1]["value"] if values else None,
            })

        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})
