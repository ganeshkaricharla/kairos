from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "assistant" | "user"
    content: str
    timestamp: datetime


class HabitPerformance(BaseModel):
    habit_id: str
    title: str
    completed_count: int
    total_days: int
    rate: float


class TrackerTrend(BaseModel):
    tracker_id: str
    name: str
    values: list[float] = []
    trend: str = "stable"


class PerformanceSnapshot(BaseModel):
    period_start: str
    period_end: str
    habits: list[HabitPerformance] = []
    tracker_trends: list[TrackerTrend] = []


class SessionSummary(BaseModel):
    """Summary of a coaching session - like 'minutes of meeting'"""
    key_points: list[str] = []  # Main discussion points
    habits_added: list[str] = []  # Habits created/modified
    next_check_in: Optional[str] = None  # When to reconnect (e.g., "in 7 days")
    action_items: list[str] = []  # Things user should do


class CoachingSession(BaseModel):
    id: str
    goal_id: str
    user_id: str = "default"
    trigger: str = "scheduled_review"
    status: str = "active"
    performance_snapshot: Optional[PerformanceSnapshot] = None
    messages: list[ChatMessage] = []
    summary: Optional[SessionSummary] = None  # Summary when session ends
    created_at: datetime
    resolved_at: Optional[datetime] = None
