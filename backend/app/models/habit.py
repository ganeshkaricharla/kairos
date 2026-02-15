from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HabitCreate(BaseModel):
    goal_id: str
    title: str
    description: str = ""
    frequency: str = "daily"
    time_of_day: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: str = "easy"
    reasoning: str = ""
    status: str = "active"
    order: int = 0
    linked_tracker_id: Optional[str] = None
    tracker_threshold: Optional[float] = None


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    replaced_by: Optional[str] = None
    replaces: Optional[str] = None
    order: Optional[int] = None
    linked_tracker_id: Optional[str] = None
    tracker_threshold: Optional[float] = None


class Habit(BaseModel):
    id: str
    goal_id: str
    user_id: str = "default"
    title: str
    description: str = ""
    frequency: str = "daily"
    time_of_day: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: str = "easy"
    reasoning: str = ""
    status: str = "active"
    activated_at: Optional[datetime] = None
    replaced_by: Optional[str] = None
    replaces: Optional[str] = None
    order: int = 0
    linked_tracker_id: Optional[str] = None
    tracker_threshold: Optional[float] = None
    created_at: datetime
    updated_at: datetime
