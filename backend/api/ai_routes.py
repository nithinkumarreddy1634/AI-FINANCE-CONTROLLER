"""
FastAPI Router for AI Controller & Audit Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from backend.services.ai_service import AIService
from ai_agent.models import HumanReviewInput, HumanDecisionEnum

ai_router = APIRouter(prefix="/api/v1", tags=["AI Finance Controller"])
ai_service = AIService()

class HumanReviewSchema(BaseModel):
    reviewer_name: str = Field(..., description="Name or ID of human reviewer")
    decision: str = Field(..., description="APPROVED, REJECTED, or MODIFIED")
    reviewer_note: str = Field(..., description="Audit note explaining decision")
    modified_status: Optional[str] = Field(None, description="Optional overridden status")

@ai_router.post("/ai/investigate-all", summary="Run AI Investigation on All Exceptions")
def investigate_all_exceptions():
    return ai_service.investigate_all_exceptions()

@ai_router.post("/ai/investigate/{transaction_id}", summary="Investigate Specific Transaction with AI")
def investigate_transaction(transaction_id: str):
    res = ai_service.investigate_transaction(transaction_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found."
        )
    return res

@ai_router.get("/ai/investigations", summary="Get All AI Investigation Results")
def get_all_investigations():
    return ai_service.investigate_all_exceptions()

@ai_router.get("/ai/investigations/{investigation_id}", summary="Get Specific AI Investigation Detail")
def get_investigation(investigation_id: str):
    res = ai_service.get_investigation_by_id(investigation_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation ID '{investigation_id}' not found."
        )
    return res

@ai_router.post("/ai/investigations/{investigation_id}/review", summary="Submit Human Review Action")
def submit_human_review(investigation_id: str, review_body: HumanReviewSchema):
    try:
        decision_enum = HumanDecisionEnum[review_body.decision.upper().strip()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be APPROVED, REJECTED, or MODIFIED."
        )

    review_input = HumanReviewInput(
        reviewer_name=review_body.reviewer_name,
        decision=decision_enum,
        reviewer_note=review_body.reviewer_note,
        modified_status=review_body.modified_status
    )

    updated_audit = ai_service.record_human_review(investigation_id, review_input)
    if not updated_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation ID '{investigation_id}' not found in audit ledger."
        )
    return {"message": "Human review recorded successfully.", "audit_record": updated_audit}

@ai_router.get("/ai/metrics", summary="Get AI Evaluation & Benchmark Metrics")
def get_ai_metrics():
    return ai_service.get_metrics()

@ai_router.get("/audit/{transaction_id}", summary="Get Transaction Audit History")
def get_transaction_audit(transaction_id: str):
    return ai_service.get_audit_trail(order_id=transaction_id)

class CopilotQuerySchema(BaseModel):
    prompt: str = Field(..., description="Query for the AI Finance Copilot")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional extra context")

@ai_router.post("/ai/copilot-chat", summary="Interactive AI Finance Copilot Chat")
def copilot_chat(query: CopilotQuerySchema):
    return ai_service.chat_copilot(query.prompt, query.context)

@ai_router.post("/ai/generate-narrative", summary="Generate Executive CFO Audit Narrative via AI")
def generate_narrative():
    return ai_service.generate_narrative_report()

