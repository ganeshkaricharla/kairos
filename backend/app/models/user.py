from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    coaching_style: str = "balanced"  # strict, balanced, supportive, scientific
    memories: list[dict] = []  # [{text: str, type: str, created_at: datetime}]

    # AI Provider Configuration (optional - falls back to global .env config)
    ai_provider: Optional[str] = None  # "openrouter", "openai", "anthropic", "custom"
    ai_api_key_encrypted: Optional[str] = None  # Encrypted API key
    ai_base_url: Optional[str] = None  # For custom endpoints
    ai_organization_id: Optional[str] = None  # For OpenAI org-specific keys

    created_at: datetime
    updated_at: datetime
