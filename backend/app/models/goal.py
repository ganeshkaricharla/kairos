from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AIContext(BaseModel):
    summary: str = ""
    plan_philosophy: str = ""
    current_phase: str = "building_foundation"
    next_review_date: Optional[str] = None
    next_session_allowed_at: Optional[datetime] = None  # Lock chat until this time


class GoalCreate(BaseModel):
    template_id: str  # ID of the goal template
    description: str  # User's custom description/context
    initial_value: Optional[float] = None  # Starting value for primary metric
    target_value: Optional[float] = None  # Target value for primary metric
    target_date: Optional[str] = None
    questionnaire_responses: dict[str, str] = {}  # question_id -> selected answer value


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None


class Goal(BaseModel):
    id: str
    user_id: str = "default"
    template_id: str  # Goal template ID
    title: str  # From template
    description: str  # User's custom description
    primary_metric_name: str  # From template (e.g., "Weight", "Study hours")
    primary_metric_unit: str  # From template (e.g., "kg", "hours")
    initial_value: Optional[float] = None  # Starting value for primary metric
    target_value: Optional[float] = None  # Target value for primary metric
    target_date: Optional[str] = None
    status: str = "active"
    ai_context: AIContext = Field(default_factory=AIContext)
    questionnaire_responses: dict[str, str] = {}  # question_id -> selected answer value
    created_at: datetime
    updated_at: datetime
