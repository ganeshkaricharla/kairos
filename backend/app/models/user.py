from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime
