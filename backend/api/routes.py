"""
FastAPI Route Definitions
Defines API endpoints for health, reconciliation execution, summary stats, transactions, and exceptions.
"""

from datetime import datetime
import io
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status
import pandas as pd

from backend.models.schemas import (
    HealthResponse, ReconciliationSummarySchema, ReconcileResponseSchema,
    TransactionResponseSchema
)
from backend.services.recon_service import ReconciliationService

router = APIRouter()
service = ReconciliationService()

@router.get("/health", response_model=HealthResponse, summary="Health Check")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/reconcile", response_model=ReconcileResponseSchema, summary="Run Reconciliation Pipeline")
async def run_reconciliation(
    orders_file: Optional[UploadFile] = File(None),
    payments_file: Optional[UploadFile] = File(None),
    bank_file: Optional[UploadFile] = File(None)
):
    try:
        if orders_file and payments_file and bank_file:
            orders_df = pd.read_csv(io.BytesIO(await orders_file.read()))
            payments_df = pd.read_csv(io.BytesIO(await payments_file.read()))
            bank_df = pd.read_csv(io.BytesIO(await bank_file.read()))
        else:
            # Fallback to local data directory files
            orders_df = pd.read_csv("data/orders.csv")
            payments_df = pd.read_csv("data/payments.csv")
            bank_df = pd.read_csv("data/bank_transactions.csv")

        summary, results = service.run_reconciliation(orders_df, payments_df, bank_df)

        return {
            "message": "Reconciliation completed successfully.",
            "summary": summary,
            "validation_errors_count": len(service.validation_errors),
            "results_file": service.results_csv_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation error: {str(e)}"
        )

@router.get("/summary", response_model=ReconciliationSummarySchema, summary="Get Summary Metrics")
def get_summary():
    return service.get_summary()

@router.get("/transactions", response_model=List[TransactionResponseSchema], summary="Get All Processed Transactions")
def get_transactions(
    status: Optional[str] = Query(None, description="Filter by status (MATCHED, AMOUNT_MISMATCH, etc.)"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score filter (0-100)"),
    search: Optional[str] = Query(None, description="Search term for order ID, customer ID, or transaction ID")
):
    return service.get_transactions(status=status, min_confidence=min_confidence, search=search)

@router.get("/exceptions", response_model=List[TransactionResponseSchema], summary="Get Exception Transactions")
def get_exceptions():
    return service.get_exceptions_list()

