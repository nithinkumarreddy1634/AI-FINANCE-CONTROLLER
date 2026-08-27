"""
Pydantic schemas for API endpoints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class TransactionResponseSchema(BaseModel):
    order_id: str
    customer_id: str
    expected_amount: float
    paid_amount: Optional[float]
    bank_received_amount: Optional[float]
    transaction_id: Optional[str]
    payment_id: Optional[str]
    bank_transaction_id: Optional[str]
    status: str
    confidence_score: float
    discrepancy_amount: float
    explanation: str
    reasons: List[str]
    order_date: Optional[str] = None
    payment_date: Optional[str] = None
    bank_date: Optional[str] = None

class ReconciliationSummarySchema(BaseModel):
    total_records: int
    matched_records: int
    unmatched_records: int
    exception_records: int
    match_rate_pct: float
    total_expected_amount: float
    total_received_amount: float
    total_discrepancy_amount: float
    duplicates_count: int
    missing_transactions_count: int
    amount_mismatches_count: int
    status_breakdown: Dict[str, int]

class ReconcileResponseSchema(BaseModel):
    message: str
    summary: ReconciliationSummarySchema
    validation_errors_count: int
    results_file: str

