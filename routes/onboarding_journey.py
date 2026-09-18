"""
Onboarding Journey Generator routes.

Provides endpoints for:
- Personalized onboarding journeys (LLM stub)
- Workflow automation hooks
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import datetime
import random

from services import vllm_client

router = APIRouter(prefix="/onboarding", tags=["Onboarding Journey Generator"])


# -------------------------------
# Request Models
# -------------------------------
class JourneyRequest(BaseModel):
    user_id: str
    role: str
    department: str


class WorkflowRequest(BaseModel):
    user_id: str
    step: str


# -------------------------------
# Endpoints
# -------------------------------

@router.post("/generate")
async def generate_onboarding(payload: Dict[str, str]):
    role = payload.get("role", "new employee")
    prompt = f"Generate a 30-day onboarding journey for a {role}."
    reply = await vllm_client.generate_text(prompt)
    return {"onboarding_plan": reply}

@router.post("/workflow/trigger")
async def trigger_workflow(req: WorkflowRequest) -> Dict[str, Any]:
    """
    Trigger workflow automation step (stub).
    Later: Replace with real BPM/automation engine (e.g., Temporal, Airflow, Camunda).
    """
    return {
        "user_id": req.user_id,
        "workflow_step": req.step,
        "status": "triggered",
        "triggered_at": datetime.datetime.utcnow().isoformat()
    }
