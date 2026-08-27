"""
FastAPI Router for Phase 3 Agent, RAG, and Investigation Timeline Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from backend.services.ai_service import AIService
from knowledge.ingestion import ingest_finance_policies

agent_router = APIRouter(prefix="/agent", tags=["Phase 3 Agentic Reasoning & RAG"])
ai_service = AIService()

@agent_router.post("/investigate/{transaction_id}", summary="Investigate Exception with Tool-Using RAG Agent")
def investigate_agent_transaction(transaction_id: str):
    res = ai_service.investigate_transaction(transaction_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found."
        )

    # Attach investigation state details
    state = ai_service.agent.states_cache.get(transaction_id) or ai_service.agent.states_cache.get(res.get("order_id", ""))
    if state:
        res["state"] = state.to_dict()

    return res

@agent_router.get("/investigations", summary="Get All Agent Investigation Results")
def get_all_agent_investigations():
    return ai_service.investigate_all_exceptions()

@agent_router.get("/investigations/{investigation_id}", summary="Get Agent Investigation Detail & State")
def get_agent_investigation_detail(investigation_id: str):
    res = ai_service.get_investigation_by_id(investigation_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation ID '{investigation_id}' not found."
        )

    state = ai_service.agent.states_cache.get(investigation_id)
    if state:
        res["state"] = state.to_dict()

    return res

@agent_router.get("/investigations/{investigation_id}/evidence", summary="Get Collected Financial Evidence Package")
def get_investigation_evidence(investigation_id: str):
    audit_log = ai_service.audit_manager.get_log_by_id(investigation_id)
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found.")

    return {
        "investigation_id": investigation_id,
        "order_id": audit_log.order_id,
        "evidence_summary": audit_log.evidence_summary
    }

@agent_router.get("/investigations/{investigation_id}/policies", summary="Get Retrieved RAG Policy Citations")
def get_investigation_policies(investigation_id: str):
    state = ai_service.agent.states_cache.get(investigation_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation state not found.")

    return {
        "investigation_id": investigation_id,
        "policy_citations": state.policy_citations
    }

@agent_router.get("/investigations/{investigation_id}/timeline", summary="Get Step-by-Step Investigation Timeline")
def get_investigation_timeline(investigation_id: str):
    state = ai_service.agent.states_cache.get(investigation_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation state not found.")

    return {
        "investigation_id": investigation_id,
        "timeline": [t.to_dict() for t in state.timeline]
    }

@agent_router.post("/rebuild-knowledge-base", summary="Rebuild Policy Vector Index")
def rebuild_knowledge_base():
    store = ingest_finance_policies()
    return {
        "message": "Knowledge base rebuilt successfully.",
        "chunks_indexed": len(store.chunks),
        "vocabulary_size": len(store.vocabulary)
    }

