from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AIContext(BaseModel):
    summary: str = ""
    plan_philosophy: str = ""
    current_phase: str = "building_foundation"
    next_review_date: Optional[str] = None


class GoalCreate(BaseModel):
    title: str
    description: str
    target_date: Optional[str] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None


class Goal(BaseModel):
    id: str
    user_id: str = "default"
    title: str
    description: str
    target_date: Optional[str] = None
    status: str = "active"
    ai_context: AIContext = Field(default_factory=AIContext)
    created_at: datetime
    updated_at: datetime
