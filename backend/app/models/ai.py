from pydantic import BaseModel


class ChangeProposal(BaseModel):
    type: str
    description: str
    details: dict = {}


class ProgressEvaluation(BaseModel):
    coaching_message: str
    proposed_changes: list[ChangeProposal] = []


class CoachingReply(BaseModel):
    message: str
    proposed_changes: list[ChangeProposal] = []
