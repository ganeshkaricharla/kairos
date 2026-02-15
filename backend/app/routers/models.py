from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import ai_service

router = APIRouter(prefix="/models", tags=["models"])


class ModelSelect(BaseModel):
    model_id: str


@router.get("")
async def list_models(search: str = Query(default="")):
    """Fetch available models from OpenRouter. Optional search filter."""
    try:
        models = await ai_service.fetch_models()
    except Exception as e:
        raise HTTPException(502, f"Failed to fetch models from OpenRouter: {e}")

    # Return a simplified list with key fields
    result = []
    for m in models:
        entry = {
            "id": m.get("id", ""),
            "name": m.get("name", ""),
            "context_length": m.get("context_length"),
            "pricing": m.get("pricing", {}),
        }
        result.append(entry)

    if search:
        search_lower = search.lower()
        result = [
            m for m in result
            if search_lower in m["id"].lower() or search_lower in m["name"].lower()
        ]

    return result


@router.get("/selected")
async def get_selected():
    """Get the currently selected model."""
    model_id = await ai_service.get_selected_model()
    return {"model_id": model_id}


@router.post("/select")
async def select_model(data: ModelSelect):
    """Select a model to use for all AI calls."""
    # Validate the model exists
    models = await ai_service.fetch_models()
    valid_ids = {m.get("id") for m in models}
    if data.model_id not in valid_ids:
        raise HTTPException(400, f"Model '{data.model_id}' not found in OpenRouter")

    await ai_service.set_selected_model(data.model_id)
    return {"model_id": data.model_id, "status": "selected"}
