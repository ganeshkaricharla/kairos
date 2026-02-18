from pydantic import BaseModel


class ProgressEvaluation(BaseModel):
    coaching_message: str


class CoachingReply(BaseModel):
    message: str
    tool_calls: list[dict] = []  # Tool calls made by AI (for UI display)
