import json
import re
import logging
from datetime import datetime, timedelta

import httpx

from app.config import settings
from app.models.ai import ProgressEvaluation, CoachingReply
from app.prompts import session_summary, goal_analysis, progress_evaluation, review_session, proactive_checkin
from app.utils.encryption import decrypt_api_key
from app.models.goal_template import get_template_by_id

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def _format_questionnaire_responses(responses: dict[str, str], template_id: str) -> str:
    """Format questionnaire responses in a human-readable format for AI."""
    if not responses or not template_id:
        return "No questionnaire data available."

    template = get_template_by_id(template_id)
    if not template or not template.questionnaire:
        return "No questionnaire data available."

    # Build formatted context
    lines = []
    for question in template.questionnaire:
        answer_value = responses.get(question.id)
        if answer_value:
            # Find the label for the selected answer
            answer_label = answer_value
            for option in question.options:
                if option.value == answer_value:
                    answer_label = option.label
                    break

            lines.append(f"- {question.question}")
            lines.append(f"  Answer: {answer_label}")

    return "\n".join(lines) if lines else "No questionnaire responses provided."

# Cached model list
_models_cache: list[dict] | None = None
_models_cache_time: datetime | None = None
_CACHE_TTL = timedelta(minutes=30)

# Selected model (persisted in DB, falls back to this)
_selected_model_id: str | None = None

# Claude models (Anthropic doesn't have a public models API)
CLAUDE_MODELS = [
    {
        "id": "claude-3-5-sonnet-20241022",
        "name": "Claude 3.5 Sonnet",
        "context_length": 200000,
        "pricing": {"prompt": "0.003", "completion": "0.015"},
    },
    {
        "id": "claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku",
        "context_length": 200000,
        "pricing": {"prompt": "0.0008", "completion": "0.004"},
    },
    {
        "id": "claude-3-opus-20240229",
        "name": "Claude 3 Opus",
        "context_length": 200000,
        "pricing": {"prompt": "0.015", "completion": "0.075"},
    },
    {
        "id": "claude-3-sonnet-20240229",
        "name": "Claude 3 Sonnet",
        "context_length": 200000,
        "pricing": {"prompt": "0.003", "completion": "0.015"},
    },
    {
        "id": "claude-3-haiku-20240307",
        "name": "Claude 3 Haiku",
        "context_length": 200000,
        "pricing": {"prompt": "0.00025", "completion": "0.00125"},
    },
]


async def fetch_models(provider: str = "openrouter", api_key: str = None, force: bool = False) -> list[dict]:
    """
    Fetch available models based on provider.

    Args:
        provider: AI provider (openrouter, openai, anthropic, custom)
        api_key: API key for the provider (optional, uses global if not provided)
        force: Force refresh cache

    Returns:
        List of model dictionaries
    """
    global _models_cache, _models_cache_time

    # For Anthropic, return hardcoded list (no public models API)
    if provider == "anthropic":
        return CLAUDE_MODELS

    # For OpenRouter and OpenAI, use cache
    if (
        not force
        and _models_cache is not None
        and _models_cache_time is not None
        and datetime.utcnow() - _models_cache_time < _CACHE_TTL
    ):
        return _models_cache

    # Determine API key to use
    if not api_key:
        if provider == "openai":
            api_key = settings.openrouter_api_key  # Will need separate OPENAI_API_KEY in future
        else:
            api_key = settings.openrouter_api_key

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Determine endpoint
    if provider == "openai":
        base_url = "https://api.openai.com/v1"
    else:
        base_url = OPENROUTER_BASE

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{base_url}/models",
            headers=headers,
        )
        logger.info(f"{provider} /models response: {response.status_code}")
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


async def _call_anthropic(system_prompt: str, user_prompt: str, model: str, api_key: str) -> str:
    """Call Anthropic's Messages API (Claude)."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": model,
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API error: {e.response.text}")
            if e.response.status_code == 401:
                raise RuntimeError("Invalid Anthropic API key. Please check your settings.")
            elif e.response.status_code == 429:
                raise RuntimeError("Anthropic rate limit exceeded. Please try again later.")
            else:
                raise RuntimeError(f"Anthropic API error: {e.response.status_code}")

        data = response.json()

    content = data["content"][0]["text"]
    logger.info(f"Anthropic Raw Response: {content!r}")
    return content


async def _call_openai_compatible(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_key: str,
    base_url: str,
    organization_id: str = None
) -> str:
    """Call OpenAI-compatible API (OpenAI, OpenRouter, or custom)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Add organization header for OpenAI if provided
    if organization_id:
        headers["OpenAI-Organization"] = organization_id

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
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
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"AI Provider error: {e.response.text}")
            if e.response.status_code == 401:
                raise RuntimeError("Invalid API key. Please check your settings.")
            elif e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded. Please try again later.")
            else:
                raise RuntimeError(f"AI Provider error: {e.response.status_code}")

        data = response.json()

    content = data["choices"][0]["message"]["content"]
    logger.info(f"AI Raw Response: {content!r}")
    return content


async def _call_with_tools(
    system_prompt: str,
    user_prompt: str,
    user_id: str = None,
    goal_id: str = None,
    tools: list[dict] = None,
    max_tool_iterations: int = 5,
    skip_personality_injection: bool = False
) -> tuple[str, list[dict]]:
    """
    Call AI with tool/function calling support.
    The AI can request data on-demand instead of receiving everything upfront.

    Args:
        skip_personality_injection: Set True if system_prompt already includes personality
            (e.g., from prompt_builder). Prevents double-injection.

    Returns:
        tuple[str, list[dict]]: (final_response, tool_calls_made)
            tool_calls_made is a list of {name, description} dicts for UI display
    """
    from app.services import ai_tools

    model = await get_selected_model()
    if not model:
        raise RuntimeError("No model selected")

    # Get AI configuration
    if user_id:
        ai_config = await get_user_ai_config(user_id)
    else:
        ai_config = {
            "provider": "openrouter",
            "api_key": settings.openrouter_api_key,
            "base_url": OPENROUTER_BASE,
        }

    if not ai_config["api_key"]:
        raise RuntimeError("No API key configured")

    # Add coaching personality (skip if already injected by prompt_builder)
    if user_id and not skip_personality_injection:
        from app.services import user_service
        from app.prompts import personalities

        user = await user_service.get_user(user_id)
        coaching_style = user.get("coaching_style", "balanced") if user else "balanced"
        personality_prompt = personalities.get_personality_prompt(coaching_style)
        system_prompt = f"{personality_prompt}\n\n{system_prompt}"

    # Build messages list
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Track tool calls for UI display
    tool_calls_made = []

    # Tool calling loop
    for iteration in range(max_tool_iterations):
        headers = {
            "Authorization": f"Bearer {ai_config['api_key']}",
            "Content-Type": "application/json",
        }

        if ai_config.get("organization_id"):
            headers["OpenAI-Organization"] = ai_config["organization_id"]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }

        # Add tools if provided (only for OpenAI-compatible APIs)
        if tools and ai_config.get("provider") != "anthropic":
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ai_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
            )

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"AI Provider error: {e.response.text}")
                raise RuntimeError(f"AI Provider error: {e.response.status_code}")

            data = response.json()

        message = data["choices"][0]["message"]

        # Check if AI wants to call tools
        if message.get("tool_calls"):
            logger.info(f"AI requested {len(message['tool_calls'])} tool calls")

            # Add assistant message to history
            messages.append(message)

            # Execute each tool call
            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])

                logger.info(f"Executing tool: {function_name} with args: {arguments}")

                # Get human-readable description for UI
                tool_def = next((t for t in (tools or []) if t["function"]["name"] == function_name), None)
                description = tool_def["function"]["description"] if tool_def else f"Requesting {function_name}"

                # Track tool call for UI display
                tool_calls_made.append({
                    "name": function_name,
                    "description": description,
                    "arguments": arguments,
                })

                # Inject user_id and goal_id if needed and not provided
                if "user_id" in arguments and not arguments["user_id"]:
                    arguments["user_id"] = user_id
                if "goal_id" in arguments and not arguments["goal_id"]:
                    arguments["goal_id"] = goal_id

                # Execute the tool
                result = await ai_tools.execute_tool(function_name, arguments)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": result,
                })

            # Continue loop to get AI's next response
            continue

        else:
            # AI didn't call any tools, return the content
            content = message.get("content", "")
            logger.info(f"AI Final Response: {content!r}")

            # Strip markdown code fences if present
            content = content.strip()
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if match:
                content = match.group(1).strip()

            return content, tool_calls_made

    # If we hit max iterations, return the last message
    logger.warning(f"Hit max tool iterations ({max_tool_iterations})")
    return messages[-1].get("content", ""), tool_calls_made


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

    # Add coaching personality to system prompt
    if user_id:
        from app.services import user_service
        from app.prompts import personalities

        user = await user_service.get_user(user_id)
        coaching_style = user.get("coaching_style", "balanced") if user else "balanced"
        personality_prompt = personalities.get_personality_prompt(coaching_style)

        # Prepend personality to system prompt
        system_prompt = f"{personality_prompt}\n\n{system_prompt}"

    # Route to appropriate API based on provider
    provider = ai_config.get("provider", "openrouter")

    if provider == "anthropic":
        content = await _call_anthropic(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            api_key=ai_config["api_key"]
        )
    else:
        # OpenAI, OpenRouter, or custom provider (all use OpenAI-compatible format)
        content = await _call_openai_compatible(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            api_key=ai_config["api_key"],
            base_url=ai_config["base_url"],
            organization_id=ai_config.get("organization_id")
        )

    # Strip markdown code fences if present
    content = content.strip()
    # Remove ```json ... ``` or just ``` ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if match:
        content = match.group(1).strip()

    return content


async def goal_setup_opening(
    title: str,
    description: str,
    primary_metric_name: str,
    primary_metric_unit: str,
    initial_value: float | None = None,
    target_value: float | None = None,
    target_date: str | None = None,
    questionnaire_responses: dict[str, str] = None,
    template_id: str = None,
    user_id: str = None
) -> CoachingReply:
    """Generate the conversational opening for a new goal setup."""
    # Format questionnaire responses for AI
    questionnaire_context = _format_questionnaire_responses(questionnaire_responses, template_id)

    user_prompt = goal_analysis.USER_PROMPT_TEMPLATE.format(
        title=title,
        description=description,
        primary_metric_name=primary_metric_name,
        primary_metric_unit=primary_metric_unit,
        initial_value=initial_value if initial_value is not None else "Not provided",
        target_value=target_value if target_value is not None else "Not provided",
        target_date=target_date if target_date else "Not set",
        questionnaire_context=questionnaire_context,
    )
    raw = await _call_openrouter(goal_analysis.SYSTEM_PROMPT, user_prompt, user_id=user_id)
    try:
        data = json.loads(raw)
        return CoachingReply(**data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise RuntimeError("Failed to process AI response. Please try again.")


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
    try:
        data = json.loads(raw)
        return ProgressEvaluation(**data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise RuntimeError("Failed to process AI evaluation. Please try again.")


async def coaching_reply_ai(
    user: dict,
    goal: dict,
    habits: list[dict],
    trackers: list[dict],
    today_logs: dict,
    chat_history: str,
    user_message: str,
    upcoming_checkins: list[dict] = None,
    use_tools: bool = True,
) -> CoachingReply:
    """
    Generate AI coaching reply using Prompt #2 (Coaching System Prompt Builder).
    Per integration guide section 4.

    Args:
        user: User document with memories and coaching_style
        goal: Goal document with ai_context
        habits: List of habit documents
        trackers: List of tracker documents
        today_logs: Today's daily log document
        chat_history: Formatted chat history
        user_message: User's latest message
        upcoming_checkins: Optional list of upcoming check-ins
        use_tools: If True, AI can request data on-demand
    """
    from app.services import ai_tools
    from app.prompts import prompt_builder

    # Build dynamic system prompt with full context (per integration guide)
    system_prompt = await prompt_builder.build_coaching_system_prompt(
        user=user,
        goal=goal,
        habits=habits,
        trackers=trackers,
        today_logs=today_logs,
        upcoming_checkins=upcoming_checkins or []
    )

    # Simple user prompt with just history and current message
    user_prompt = f"""Chat History:
{chat_history}

User's Latest Message: {user_message}

Respond with ONLY valid JSON:
{{
  "message": "Your response with any action tags embedded inline"
}}"""

    # Use tool calling if enabled
    tool_calls_made = []
    goal_id = goal["id"]
    user_id = user["id"]

    if use_tools and goal_id:
        raw, tool_calls_made = await _call_with_tools(
            system_prompt,
            user_prompt,
            user_id=user_id,
            goal_id=goal_id,
            tools=ai_tools.AVAILABLE_TOOLS,
            skip_personality_injection=True  # Prompt builder already includes personality
        )
    else:
        # Fall back to simple call without tools
        # Note: _call_openrouter will add personality, but that's okay for non-builder prompts
        raw = await _call_openrouter(system_prompt, user_prompt, user_id=user_id)

    try:
        data = json.loads(raw)
        # Add tool calls to the response
        data["tool_calls"] = tool_calls_made
        return CoachingReply(**data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise RuntimeError("Failed to process AI response. Please try again.")


async def initial_session_reply(
    user: dict,
    goal: dict,
    conversation_history: str,
    current_phase: str,
    questionnaire_responses: dict,
    template_id: str = None,
) -> dict:
    """
    Generate AI reply for Prompt #1 (Initial Session).
    Handles goal setup with 3-phase conversation (exploring → proposing → creating → complete).
    Per integration guide section 3.

    Returns:
        dict with keys: phase (str), message (str)
    """
    from app.prompts import initial_session, personalities
    from datetime import date as dt_date

    # Get coaching style fragment
    coaching_style = user.get("coaching_style", "balanced")
    coaching_style_fragment = personalities.get_personality_prompt(coaching_style)

    # Format questionnaire context
    questionnaire_context = _format_questionnaire_responses(questionnaire_responses, template_id)

    # Calculate gap and days remaining
    initial = goal.get("initial_value", 0)
    target = goal.get("target_value", 0)
    gap = target - initial

    days_remaining = 0
    if goal.get("target_date"):
        try:
            target_date = dt_date.fromisoformat(goal["target_date"])
            days_remaining = (target_date - dt_date.today()).days
        except:
            pass

    # Build user prompt
    user_prompt = initial_session.INITIAL_SESSION_USER_PROMPT.format(
        title=goal.get("title", ""),
        description=goal.get("description", ""),
        primary_metric_name=goal.get("primary_metric_name", ""),
        primary_metric_unit=goal.get("primary_metric_unit", ""),
        initial_value=initial,
        target_value=target,
        target_date=goal.get("target_date", "Not set"),
        gap=gap,
        days_remaining=days_remaining,
        coaching_style_fragment=coaching_style_fragment,
        questionnaire_context=questionnaire_context,
        conversation_history=conversation_history or "(Session just started — Priya speaks first)",
        current_phase=current_phase.upper() if current_phase else "EXPLORING"
    )

    # Call AI (no tools needed for initial session)
    raw = await _call_openrouter(
        initial_session.INITIAL_SESSION_SYSTEM_PROMPT,
        user_prompt,
        user_id=user["id"]
    )

    try:
        data = json.loads(raw)
        return data  # {phase: str, message: str}
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse initial session response: {e}")
        raise RuntimeError("Failed to process AI response. Please try again.")


async def review_session_reply(
    user: dict,
    goal: dict,
    habits: list[dict],
    trackers: list[dict],
    conversation_history: str,
    trigger_type: str,
    trigger_reason: str,
    review_stage: str = "opening",
) -> dict:
    """
    Generate AI reply for Prompt #4 (Review Session).
    Handles scheduled and data-triggered review sessions.
    Per integration guide section 6.

    Args:
        user: User document with memories and coaching_style
        goal: Goal document with ai_context
        habits: List of active habit documents
        trackers: List of tracker documents
        conversation_history: Formatted chat history for this review
        trigger_type: scheduled | streak_broken | consistently_missing | etc.
        trigger_reason: Human-readable explanation of why review triggered
        review_stage: opening | mid_conversation | proposing_change | closing

    Returns:
        dict with keys: review_type (str), message (str)
    """
    from app.prompts import personalities
    from datetime import date as dt_date

    # Get coaching style fragment
    coaching_style = user.get("coaching_style", "balanced")
    coaching_style_fragment = personalities.get_personality_prompt(coaching_style)

    # Build memories section
    memories = user.get("memories", [])
    if memories:
        memories_section = "What you know about this person:\n"
        for mem in memories[:20]:  # Top 20 memories
            memories_section += f"- {mem.get('text', '')}\n"
    else:
        memories_section = "No prior memories saved yet."

    # Calculate days remaining and current value
    days_remaining = 0
    if goal.get("target_date"):
        try:
            target_date = dt_date.fromisoformat(goal["target_date"])
            days_remaining = (target_date - dt_date.today()).days
        except:
            pass

    # Get current value from most recent tracker log (simplified)
    current_value = goal.get("initial_value", 0)

    # Calculate timeline health
    initial_value = goal.get("initial_value", 0)
    target_value = goal.get("target_value", 0)
    created_at = goal.get("created_at", "")

    try:
        created_date = dt_date.fromisoformat(created_at.split("T")[0])
        days_elapsed = (dt_date.today() - created_date).days
    except:
        days_elapsed = 7

    direction = goal.get("direction", "increase")
    timeline_health, pace_note = review_session.build_timeline_health(
        current_value=current_value,
        target_value=target_value,
        initial_value=initial_value,
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        direction=direction
    )

    # Build habits summary
    habits_summary = review_session.build_habits_summary_for_review(habits, period_days=7)

    # Build tracker summary (simplified - would need actual data)
    period_averages = {}
    prior_period_averages = {}
    tracker_summary = review_session.build_tracker_summary_for_review(
        trackers,
        period_averages,
        prior_period_averages
    )

    # Get task instruction based on stage
    task_instruction = review_session.get_review_task_instruction(review_stage)

    # Build user prompt
    user_prompt = review_session.REVIEW_SESSION_USER_PROMPT.format(
        trigger_type=trigger_type,
        trigger_reason=trigger_reason,
        coaching_style_fragment=coaching_style_fragment,
        memories_section=memories_section,
        goal_title=goal.get("title", ""),
        goal_description=goal.get("description", ""),
        current_phase=goal.get("ai_context", {}).get("current_phase", "building_foundation"),
        target_date=goal.get("target_date", "Not set"),
        days_remaining=days_remaining,
        primary_metric_name=goal.get("primary_metric_name", ""),
        current_value=current_value,
        target_value=target_value,
        primary_metric_unit=goal.get("primary_metric_unit", ""),
        timeline_health=timeline_health,
        pace_note=pace_note,
        habits_summary=habits_summary,
        tracker_summary=tracker_summary,
        conversation_history=conversation_history or "(Review session just started)",
        task_instruction=task_instruction
    )

    # Call AI (no tools needed for review session initially)
    raw = await _call_openrouter(
        review_session.REVIEW_SESSION_SYSTEM_PROMPT,
        user_prompt,
        user_id=user["id"]
    )

    try:
        data = json.loads(raw)
        return data  # {review_type: str, message: str}
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse review session response: {e}")
        raise RuntimeError("Failed to process AI response. Please try again.")


async def proactive_checkin_reply(
    user: dict,
    goal: dict,
    habits: list[dict],
    trackers: list[dict],
    trigger_type: str,
    trigger_details: dict,
) -> dict:
    """
    Generate AI proactive check-in message for Prompt #5.
    Runs async in background, delivers as push notification or waiting message.
    Per integration guide section 7.

    Args:
        user: User document with memories and coaching_style
        goal: Goal document with ai_context
        habits: List of active habit documents
        trackers: List of tracker documents
        trigger_type: missed_3_plus_days | habit_formed | metric_wrong_direction
        trigger_details: Dict with trigger-specific context (habit, metric, etc.)

    Returns:
        dict with keys: trigger_type, metric_case, delivery, message
    """
    from app.prompts import personalities

    # Get coaching style fragment
    coaching_style = user.get("coaching_style", "balanced")
    coaching_style_fragment = personalities.get_personality_prompt(coaching_style)

    # Build memories section
    memories = user.get("memories", [])
    if memories:
        memories_section = "What you know:\n"
        for mem in memories[:15]:  # Top 15 memories
            memories_section += f"- {mem.get('text', '')}\n"
    else:
        memories_section = "No memories yet."

    # Build trigger-specific context using helper
    trigger_context = proactive_checkin.build_trigger_context(
        trigger_type=trigger_type,
        trigger_details=trigger_details,
        habits=habits,
        trackers=trackers,
        goal=goal
    )

    # Detect metric context flag if needed
    context_flag = "none"
    if trigger_type == "metric_wrong_direction":
        context_flag = personalities.detect_metric_context_flag(memories)

    # Get previous proactive messages (to avoid repetition)
    previous_messages = user.get("previous_proactive_messages", [])
    previous_context = "\n".join(
        f"- {msg['trigger_type']}: {msg['message'][:80]}..."
        for msg in previous_messages[-3:]  # Last 3 messages
    ) if previous_messages else "No previous proactive messages"

    # Build user prompt
    user_prompt = proactive_checkin.PROACTIVE_CHECKIN_USER_PROMPT.format(
        trigger_type=trigger_type,
        trigger_context=trigger_context,
        coaching_style_fragment=coaching_style_fragment,
        memories_section=memories_section,
        goal_title=goal.get("title", ""),
        goal_description=goal.get("description", ""),
        current_phase=goal.get("ai_context", {}).get("current_phase", "building_foundation"),
        context_flag=context_flag,
        previous_proactive_messages=previous_context,
    )

    # Call AI (no tools for proactive messages)
    raw = await _call_openrouter(
        proactive_checkin.PROACTIVE_CHECKIN_SYSTEM_PROMPT,
        user_prompt,
        user_id=user["id"]
    )

    try:
        data = json.loads(raw)
        return data  # {trigger_type, metric_case, delivery, message}
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse proactive checkin response: {e}")
        raise RuntimeError("Failed to process AI response. Please try again.")


async def generate_session_summary(
    goal_title: str,
    chat_history: str,
    user_id: str = None,
) -> dict:
    """Generate a summary of the coaching session - like 'minutes of meeting'."""
    user_prompt = session_summary.USER_PROMPT_TEMPLATE.format(
        goal_title=goal_title,
        chat_history=chat_history,
    )
    raw = await _call_openrouter(session_summary.SYSTEM_PROMPT, user_prompt, user_id=user_id)
    try:
        data = json.loads(raw)
        return data
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse session summary: {e}")
        # Return a basic fallback summary
        return {
            "key_points": ["Coaching session completed"],
            "habits_added": [],
            "next_check_in": None,
            "action_items": ["Continue tracking your habits"],
        }
