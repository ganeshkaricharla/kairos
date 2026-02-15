"""User profile and preferences API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.services import user_service
from app.prompts.personalities import list_personalities


router = APIRouter(prefix="/users", tags=["users"])


class CoachingStyleUpdate(BaseModel):
    """Request model for updating coaching style."""
    style: str


class MemoryCreate(BaseModel):
    """Request model for creating a memory."""
    text: str
    type: str = "general"


class AIConfigUpdate(BaseModel):
    """Request model for updating AI configuration."""
    provider: str  # openrouter, openai, anthropic, custom
    api_key: str
    base_url: str | None = None
    organization_id: str | None = None


class AIConfigTest(BaseModel):
    """Request model for testing AI configuration."""
    provider: str
    api_key: str
    base_url: str | None = None


@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile including coaching style and memories.

    Returns:
        User profile with id, email, name, coaching_style, memories, etc.
    """
    user = await user_service.get_user(current_user["id"])
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.get("/personalities")
async def get_coaching_personalities():
    """
    Get list of available coaching personalities.

    Returns:
        List of personality options with id, name, description, and tone
    """
    return list_personalities()


@router.patch("/me/coaching-style")
async def update_user_coaching_style(
    data: CoachingStyleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user's coaching personality preference.

    Args:
        data: Coaching style update (strict, balanced, supportive, scientific)

    Returns:
        Updated user profile

    Raises:
        HTTPException: If style is invalid
    """
    try:
        user = await user_service.update_coaching_style(current_user["id"], data.style)
        return user
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/me/memories")
async def create_memory(
    data: MemoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a memory about the user.

    Args:
        data: Memory text and type (preference, schedule, motivation, challenge, general)

    Returns:
        Updated user profile with new memory
    """
    user = await user_service.add_memory(current_user["id"], data.text, data.type)
    return user


@router.get("/me/memories")
async def get_user_memories(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get recent memories for the current user.

    Args:
        limit: Maximum number of memories to return (default: 10)

    Returns:
        List of recent memories
    """
    memories = await user_service.get_memories(current_user["id"], limit)
    return {"memories": memories}


@router.delete("/me/memories/{index}")
async def delete_user_memory(
    index: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a memory by index.

    Args:
        index: Memory index to delete (0-based)

    Returns:
        Updated user profile

    Raises:
        HTTPException: If index is out of range
    """
    try:
        user = await user_service.delete_memory(current_user["id"], index)
        return user
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/me/ai-config")
async def get_user_ai_config(current_user: dict = Depends(get_current_user)):
    """
    Get current user's AI provider configuration (with masked API key).

    Returns:
        AI config with provider, masked API key, base_url, etc.
        Returns using_global_key=True if user hasn't configured their own key.
    """
    config = await user_service.get_ai_config(current_user["id"])
    return config


@router.patch("/me/ai-config")
async def update_user_ai_config(
    data: AIConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user's AI provider configuration.

    Args:
        data: Provider type, API key, optional base URL and org ID

    Returns:
        Updated user profile with masked API key

    Raises:
        HTTPException: If provider or API key is invalid
    """
    try:
        user = await user_service.update_ai_config(
            current_user["id"],
            data.provider,
            data.api_key,
            data.base_url,
            data.organization_id
        )
        return user
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/me/ai-config")
async def delete_user_ai_config(current_user: dict = Depends(get_current_user)):
    """
    Delete user's AI configuration and revert to global key.

    Returns:
        Updated user profile
    """
    user = await user_service.delete_ai_config(current_user["id"])
    return user


@router.post("/me/ai-config/test")
async def test_user_ai_config(data: AIConfigTest):
    """
    Test an AI configuration before saving.

    Args:
        data: Provider, API key, and optional base URL to test

    Returns:
        Test result with success status and message
    """
    result = await user_service.test_ai_config(
        data.provider,
        data.api_key,
        data.base_url
    )
    return result
