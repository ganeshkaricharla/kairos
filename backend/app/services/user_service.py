"""User service for managing user preferences, coaching style, and memories."""
from bson import ObjectId
from datetime import datetime
import httpx

from app.database import get_db
from app.utils.object_id import doc_id
from app.utils.dates import now
from app.utils.encryption import encrypt_api_key, decrypt_api_key, mask_api_key


async def get_user(user_id: str) -> dict | None:
    """
    Get user by ID.

    Args:
        user_id: User ID string

    Returns:
        User document with id field, or None if not found
    """
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return doc_id(user) if user else None


async def update_coaching_style(user_id: str, style: str) -> dict:
    """
    Update user's coaching personality preference.

    Args:
        user_id: User ID string
        style: Coaching style (strict, balanced, supportive, scientific)

    Returns:
        Updated user document

    Raises:
        ValueError: If style is not valid
    """
    valid_styles = ["strict", "balanced", "supportive", "scientific"]
    if style not in valid_styles:
        raise ValueError(f"Invalid coaching style. Must be one of: {', '.join(valid_styles)}")

    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"coaching_style": style, "updated_at": now()}}
    )
    return await get_user(user_id)


async def add_memory(user_id: str, text: str, memory_type: str = "general") -> dict:
    """
    Add a memory to user's profile.

    Args:
        user_id: User ID string
        text: Memory content
        memory_type: Type of memory (preference, schedule, motivation, challenge, general)

    Returns:
        Updated user document
    """
    db = get_db()

    memory = {
        "text": text,
        "type": memory_type,
        "created_at": now()
    }

    # Limit memories to 100 (remove oldest if exceeding)
    user = await get_user(user_id)
    current_memories = user.get("memories", [])

    if len(current_memories) >= 100:
        # Remove oldest memory
        current_memories = current_memories[1:]

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$push": {"memories": memory},
            "$set": {"updated_at": now()}
        }
    )

    # If we need to remove oldest, do it in a separate update
    if len(current_memories) >= 100:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pop": {"memories": -1}}  # Remove first element
        )

    return await get_user(user_id)


async def delete_memory(user_id: str, memory_index: int) -> dict:
    """
    Remove a memory by index.

    Args:
        user_id: User ID string
        memory_index: Index of memory to remove (0-based)

    Returns:
        Updated user document

    Raises:
        ValueError: If index is out of range
    """
    db = get_db()
    user = await get_user(user_id)

    if not user:
        raise ValueError("User not found")

    memories = user.get("memories", [])

    if memory_index < 0 or memory_index >= len(memories):
        raise ValueError(f"Memory index {memory_index} out of range (0-{len(memories)-1})")

    # Remove memory at index
    memories.pop(memory_index)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"memories": memories, "updated_at": now()}}
    )

    return await get_user(user_id)


async def get_memories(user_id: str, limit: int = 10) -> list[dict]:
    """
    Get recent memories for a user.

    Args:
        user_id: User ID string
        limit: Maximum number of memories to return (default: 10)

    Returns:
        List of most recent memories
    """
    user = await get_user(user_id)
    if not user:
        return []

    memories = user.get("memories", [])
    # Return last N memories (most recent)
    return memories[-limit:] if len(memories) > limit else memories


async def update_ai_config(
    user_id: str,
    provider: str,
    api_key: str,
    base_url: str | None = None,
    organization_id: str | None = None
) -> dict:
    """
    Update user's AI provider configuration.

    Args:
        user_id: User ID string
        provider: Provider name (openrouter, openai, anthropic, custom)
        api_key: API key (will be encrypted before storage)
        base_url: Optional custom base URL
        organization_id: Optional OpenAI organization ID

    Returns:
        Updated user document (with masked API key)

    Raises:
        ValueError: If provider or API key is invalid
    """
    valid_providers = ["openrouter", "openai", "anthropic", "custom"]
    if provider not in valid_providers:
        raise ValueError(f"Invalid provider. Must be one of: {', '.join(valid_providers)}")

    if not api_key:
        raise ValueError("API key is required")

    db = get_db()
    encrypted_key = encrypt_api_key(api_key)

    update_data = {
        "ai_provider": provider,
        "ai_api_key_encrypted": encrypted_key,
        "updated_at": now()
    }

    if base_url:
        update_data["ai_base_url"] = base_url
    if organization_id:
        update_data["ai_organization_id"] = organization_id

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    user = await get_user(user_id)
    # Return with masked API key
    if user:
        user["ai_api_key_masked"] = mask_api_key(api_key)
        user.pop("ai_api_key_encrypted", None)
    return user


async def get_ai_config(user_id: str) -> dict:
    """
    Get user's AI configuration with masked API key.

    Args:
        user_id: User ID string

    Returns:
        Dict with provider, masked API key, base_url, etc.
        Returns using_global_key=True if user hasn't configured their own key.
    """
    user = await get_user(user_id)

    if not user or not user.get("ai_api_key_encrypted"):
        return {
            "provider": None,
            "api_key_masked": None,
            "base_url": None,
            "organization_id": None,
            "using_global_key": True,
        }

    decrypted_key = decrypt_api_key(user["ai_api_key_encrypted"])

    return {
        "provider": user.get("ai_provider"),
        "api_key_masked": mask_api_key(decrypted_key),
        "base_url": user.get("ai_base_url"),
        "organization_id": user.get("ai_organization_id"),
        "using_global_key": False,
    }


async def delete_ai_config(user_id: str) -> dict:
    """
    Delete user's AI configuration (revert to global key).

    Args:
        user_id: User ID string

    Returns:
        Updated user document
    """
    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$unset": {
                "ai_provider": "",
                "ai_api_key_encrypted": "",
                "ai_base_url": "",
                "ai_organization_id": "",
            },
            "$set": {"updated_at": now()}
        }
    )
    return await get_user(user_id)


async def test_ai_config(provider: str, api_key: str, base_url: str | None = None) -> dict:
    """
    Test an AI configuration by making a simple API call.

    Args:
        provider: Provider name
        api_key: API key to test
        base_url: Optional custom base URL

    Returns:
        Dict with success status, message, and error (if any)
    """
    if not base_url:
        urls = {
            "openrouter": "https://openrouter.ai/api/v1",
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
        }
        base_url = urls.get(provider, "https://openrouter.ai/api/v1")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "API key is valid and working",
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "message": "API key validation failed",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to connect to API",
            "error": str(e)
        }
