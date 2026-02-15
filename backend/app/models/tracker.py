from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TrackerCreate(BaseModel):
    goal_id: str
    name: str
    description: str = ""
    unit: str = ""
    type: str = "main"
    direction: str = "increase"
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    reasoning: str = ""


class TrackerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None


class Tracker(BaseModel):
    id: str
    goal_id: str
    user_id: str = "default"
    name: str
    description: str = ""
    unit: str = ""
    type: str = "main"
    direction: str = "increase"
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    reasoning: str = ""
    created_at: datetime
    updated_at: datetime
