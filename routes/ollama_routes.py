"""
Ollama status and health check endpoints.
Allows the frontend to check if Ollama is running and which models are available.
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/ollama", tags=["Ollama AI"])


@router.get("/status")
async def ollama_status() -> Dict[str, Any]:
    """
    Check if Ollama server is running and return available models.
    Called by the frontend status bar to show AI availability.
    """
    try:
        from services.llm_utils import health_check
        return await health_check()
    except Exception as e:
        return {
            "status": "error",
            "models": [],
            "current_model": "mistral",
            "endpoint": "http://localhost:11434/api",
            "message": f"Health check failed: {str(e)}"
        }


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    List all available Ollama models.
    """
    import os
    import httpx
    base_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api")
    base_url = base_url.rstrip("/api").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return {"models": models, "status": "ok"}
            return {"models": [], "status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {
            "models": [],
            "status": "error",
            "message": str(e)
        }
