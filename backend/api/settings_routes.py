"""
FastAPI Router for System Settings, LLM / OpenRouter Configuration, and Live Diagnostics
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.ai_service import AIService
from ai_agent.providers.llm_provider import LLMAIProvider

settings_router = APIRouter(prefix="/api/v1/settings", tags=["System Settings & AI Configuration"])
ai_service = AIService()

class SettingsUpdateRequest(BaseModel):
    settlement_window_days: Optional[int] = Field(default=3, ge=1, le=30)
    auto_reconcile_threshold: Optional[float] = Field(default=90.0, ge=50.0, le=100.0)
    human_review_threshold: Optional[float] = Field(default=70.0, ge=30.0, le=95.0)
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None

class LLMTestRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = "openrouter/auto"

@settings_router.get("", summary="Get Current System Settings & AI Configuration")
def get_settings():
    key = os.getenv("OPENROUTER_API_KEY", "")
    masked_key = f"{key[:10]}...{key[-4:]}" if len(key) > 15 else ("Configured" if key else "Not Set")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    return {
        "settlement_window_days": 3,
        "auto_reconcile_threshold": 90.0,
        "human_review_threshold": 70.0,
        "ai_provider": "OpenRouter" if key else "Deterministic Engine",
        "openrouter_model": model,
        "openrouter_key_status": "Active" if key else "Unset",
        "masked_key": masked_key,
        "render_backend_url": os.getenv("RENDER_SERVICE_URL", "https://ai-finance-controller-jnc0.onrender.com"),
        "render_service_id": os.getenv("RENDER_SERVICE_ID", "srv-daro718jo6nc738p9a1g")
    }

@settings_router.post("", summary="Update System Settings & OpenRouter Key")
def update_settings(req: SettingsUpdateRequest):
    if req.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = req.openrouter_api_key.strip()
    if req.openrouter_model:
        os.environ["OPENROUTER_MODEL"] = req.openrouter_model.strip()

    # Re-initialize agent provider if key is provided
    active_key = os.getenv("OPENROUTER_API_KEY")
    active_model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    if active_key:
        ai_service.agent.provider = LLMAIProvider(api_key=active_key, provider_name="openrouter", model=active_model)

    return {
        "status": "SUCCESS",
        "message": "System and AI settings updated successfully.",
        "active_model": active_model
    }

@settings_router.post("/test-llm", summary="Test OpenRouter API Key Live Connection")
def test_openrouter_connection(req: LLMTestRequest):
    key = req.api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OpenRouter API key provided or found in environment."
        )

    model = req.model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    test_url = "https://openrouter.ai/api/v1/auth/key"
    headers = {"Authorization": f"Bearer {key}"}
    req_obj = urllib.request.Request(test_url, headers=headers)

    try:
        with urllib.request.urlopen(req_obj, timeout=8) as resp:
            auth_data = json.loads(resp.read().decode("utf-8"))
            data = auth_data.get("data", {})
            free_reqs = data.get("free_model_daily_requests", {})
            return {
                "status": "CONNECTED",
                "label": data.get("label", "OpenRouter User"),
                "is_free_tier": data.get("is_free_tier", True),
                "remaining_free_requests": free_reqs.get("remaining", "Unlimited"),
                "model": model,
                "message": f"Successfully connected to OpenRouter. Ready for AI investigations with '{model}'."
            }
    except urllib.error.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OpenRouter Authentication Failed (HTTP {e.code}): Invalid API Key."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )
