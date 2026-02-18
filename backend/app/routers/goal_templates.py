from fastapi import APIRouter

from app.models.goal_template import GOAL_TEMPLATES

router = APIRouter(prefix="/goal-templates", tags=["goal-templates"])


@router.get("")
async def list_goal_templates():
    """Get all available goal templates."""
    return GOAL_TEMPLATES
