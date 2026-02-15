from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "assistant" | "user"
    content: str
    timestamp: datetime


class ProposedChange(BaseModel):
    type: str  # add_habit, swap_habit, upgrade_intensity, downgrade_intensity, pause_habit, add_tracker
    description: str
    details: dict[str, Any] = {}
    accepted: Optional[bool] = None


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


class CoachingSession(BaseModel):
    id: str
    goal_id: str
    user_id: str = "default"
    trigger: str = "scheduled_review"
    status: str = "active"
    performance_snapshot: Optional[PerformanceSnapshot] = None
    messages: list[ChatMessage] = []
    proposed_changes: list[ProposedChange] = []
    created_at: datetime
    resolved_at: Optional[datetime] = None
