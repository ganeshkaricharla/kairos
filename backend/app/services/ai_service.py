import json
import logging
from datetime import datetime, timedelta

import httpx

from app.config import settings
from app.models.ai import ProgressEvaluation, CoachingReply
from app.prompts import goal_analysis, progress_evaluation, coaching_reply
from app.utils.encryption import decrypt_api_key

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Cached model list
_models_cache: list[dict] | None = None
_models_cache_time: datetime | None = None
_CACHE_TTL = timedelta(minutes=30)

# Selected model (persisted in DB, falls back to this)
_selected_model_id: str | None = None


async def fetch_models(force: bool = False) -> list[dict]:
    """Fetch available models from OpenRouter /v1/models API, with caching."""
    global _models_cache, _models_cache_time

    if (
        not force
        and _models_cache is not None
        and _models_cache_time is not None
        and datetime.utcnow() - _models_cache_time < _CACHE_TTL
    ):
        return _models_cache

    headers = {}
    if settings.openrouter_api_key:
        headers["Authorization"] = f"Bearer {settings.openrouter_api_key}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{OPENROUTER_BASE}/models",
            headers=headers,
        )
        logger.info(f"OpenRouter /models response: {response.status_code}")
        response.raise_for_status()
        data = response.json()

    models = data.get("data", [])
    _models_cache = models
    _models_cache_time = datetime.utcnow()
    return models


async def get_selected_model() -> str | None:
    """Get the currently selected model ID."""
    global _selected_model_id
    if _selected_model_id:
        return _selected_model_id

    # Try loading from DB
    from app.database import get_db
    db = get_db()
    if db is not None:
        doc = await db.settings.find_one({"key": "selected_model"})
        if doc:
            _selected_model_id = doc["value"]
            return _selected_model_id

    return None


async def set_selected_model(model_id: str) -> None:
    """Set the model to use for AI calls. Persisted in DB."""
    global _selected_model_id
    _selected_model_id = model_id

    from app.database import get_db
    db = get_db()
    if db is not None:
        await db.settings.update_one(
            {"key": "selected_model"},
            {"$set": {"key": "selected_model", "value": model_id}},
            upsert=True,
        )


def _get_default_base_url(provider: str) -> str:
    """Get default base URL for a provider."""
    urls = {
        "openrouter": "https://openrouter.ai/api/v1",
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }
    return urls.get(provider, "https://openrouter.ai/api/v1")


async def get_user_ai_config(user_id: str) -> dict:
    """
    Get AI configuration for a specific user.
    Falls back to global config if user hasn't configured their own.

    Returns:
        Dict with provider, api_key, base_url, organization_id
    """
    from app.services import user_service

    user = await user_service.get_user(user_id)

    # If user has configured their own API key, use it
    if user and user.get("ai_api_key_encrypted"):
        return {
            "provider": user.get("ai_provider", "openrouter"),
            "api_key": decrypt_api_key(user["ai_api_key_encrypted"]),
            "base_url": user.get("ai_base_url") or _get_default_base_url(user.get("ai_provider")),
            "organization_id": user.get("ai_organization_id"),
        }

    # Fall back to global OpenRouter config
    return {
        "provider": "openrouter",
        "api_key": settings.openrouter_api_key,
        "base_url": OPENROUTER_BASE,
        "organization_id": None,
    }


async def _call_openrouter(system_prompt: str, user_prompt: str, user_id: str = None) -> str:
    """Call AI provider with user-specific or global configuration."""
    model = await get_selected_model()
    if not model:
        raise RuntimeError(
            "No model selected. Use GET /models to list available models "
            "and POST /models/select to choose one."
        )

    # Get AI configuration (user-specific or global)
    if user_id:
        ai_config = await get_user_ai_config(user_id)
    else:
        ai_config = {
            "provider": "openrouter",
            "api_key": settings.openrouter_api_key,
            "base_url": OPENROUTER_BASE,
        }

    if not ai_config["api_key"]:
        raise RuntimeError(
            "No API key configured. Please add your API key in Settings."
        )

    headers = {
        "Authorization": f"Bearer {ai_config['api_key']}",
        "Content-Type": "application/json",
    }

    # Add organization header for OpenAI if provided
    if ai_config.get("organization_id"):
        headers["OpenAI-Organization"] = ai_config["organization_id"]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ai_config['base_url']}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        first_newline = content.index("\n")
        content = content[first_newline + 1:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


async def goal_setup_opening(
    title: str, description: str, target_date: str | None = None, user_id: str = None
) -> CoachingReply:
    """Generate the conversational opening for a new goal setup."""
    target_section = f"**Target Date:** {target_date}" if target_date else ""
    user_prompt = goal_analysis.USER_PROMPT_TEMPLATE.format(
        title=title,
        description=description,
        target_date_section=target_section,
    )
    raw = await _call_openrouter(goal_analysis.SYSTEM_PROMPT, user_prompt, user_id=user_id)
    data = json.loads(raw)
    return CoachingReply(**data)


async def evaluate_progress(
    goal_title: str,
    goal_description: str,
    current_phase: str,
    period_start: str,
    period_end: str,
    habits_summary: str,
    tracker_summary: str,
    user_id: str = None,
) -> ProgressEvaluation:
    user_prompt = progress_evaluation.USER_PROMPT_TEMPLATE.format(
        goal_title=goal_title,
        goal_description=goal_description,
        current_phase=current_phase,
        period_start=period_start,
        period_end=period_end,
        habits_summary=habits_summary,
        tracker_summary=tracker_summary,
    )
    raw = await _call_openrouter(progress_evaluation.SYSTEM_PROMPT, user_prompt, user_id=user_id)
    data = json.loads(raw)
    return ProgressEvaluation(**data)


async def coaching_reply_ai(
    goal_title: str,
    current_phase: str,
    performance_summary: str,
    active_habits_trackers: str,
    pending_changes: str,
    chat_history: str,
    user_message: str,
    user_id: str = None,
) -> CoachingReply:
    user_prompt = coaching_reply.USER_PROMPT_TEMPLATE.format(
        goal_title=goal_title,
        current_phase=current_phase,
        performance_summary=performance_summary,
        active_habits_trackers=active_habits_trackers,
        pending_changes=pending_changes,
        chat_history=chat_history,
        user_message=user_message,
    )
    raw = await _call_openrouter(coaching_reply.SYSTEM_PROMPT, user_prompt, user_id=user_id)
    data = json.loads(raw)
    return CoachingReply(**data)
