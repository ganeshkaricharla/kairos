from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HabitCompletion(BaseModel):
    habit_id: str
    completed: bool = False
    completed_at: Optional[datetime] = None
    notes: str = ""


class TrackerEntry(BaseModel):
    tracker_id: str
    value: float
    logged_at: Optional[datetime] = None
    notes: str = ""


class TrackerLogInput(BaseModel):
    value: float
    notes: str = ""


class DailyLog(BaseModel):
    id: str
    user_id: str = "default"
    goal_id: str
    date: str
    habit_completions: list[HabitCompletion] = []
    tracker_entries: list[TrackerEntry] = []
    created_at: datetime
    updated_at: datetime
