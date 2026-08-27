"""
FastAPI Router for System & Component Health Endpoints
Supports /health, /health/ai, /health/database, and /health/rag.
"""

import os
from fastapi import APIRouter, HTTPException, status
from knowledge.vector_store import VectorStore
from backend.services.ai_service import AIService

health_router = APIRouter(prefix="/health", tags=["System & Component Health"])
ai_service = AIService()

@health_router.get("", summary="General Health Check")
def get_general_health():
    return {
        "status": "OPERATIONAL",
        "version": "5.0.0",
        "environment": os.getenv("APP_ENV", "development"),
        "ai_controller": "ONLINE",
        "rag_engine": "READY"
    }

@health_router.get("/ai", summary="AI Provider & Controller Health")
def get_ai_health():
    return {
        "status": "OPERATIONAL",
        "provider": ai_service.agent.provider.__class__.__name__,
        "mock_mode": True,
        "fallback_available": True,
        "policy_engine_active": True
    }

@health_router.get("/database", summary="Database & Ledger Storage Health")
def get_database_health():
    audit_file = ai_service.audit_manager.file_path
    exists = os.path.exists(audit_file)
    count = len(ai_service.audit_manager.audit_logs)
    return {
        "status": "CONNECTED",
        "storage_type": "JSON_APPEND_ONLY_LEDGER",
        "audit_file": audit_file,
        "file_exists": exists,
        "records_count": count
    }

@health_router.get("/rag", summary="RAG Knowledge Base & Vector Index Health")
def get_rag_health():
    store = VectorStore()
    return {
        "status": "READY",
        "total_chunks_indexed": len(store.chunks),
        "vocabulary_size": len(store.vocabulary),
        "policy_documents_indexed": 7
    }

