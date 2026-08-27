"""
FastAPI Router for Exportable Reports (CSV and JSON)
Supports downloading Reconciliation Summary, Exceptions Ledger, AI Investigations, and Audit Trail.
"""

import io
from typing import List, Dict, Any
from fastapi import APIRouter, Response, HTTPException, status
import pandas as pd

from backend.services.recon_service import ReconciliationService
from backend.services.ai_service import AIService
from reconciliation.models import ReconciliationStatus

report_router = APIRouter(prefix="/api/v1/reports", tags=["Exportable Reports"])
recon_service = ReconciliationService()
ai_service = AIService()

@report_router.get("/summary/json", summary="Get Summary Report (JSON)")
def get_summary_report_json():
    return recon_service.get_summary()

@report_router.get("/summary/csv", summary="Export Reconciliation Results (CSV)")
def export_results_csv():
    results = recon_service.latest_results
    if not results:
        recon_service.initialize_default_run()
        results = recon_service.latest_results

    data = []
    for r in results:
        data.append({
            "Order ID": r.order_id,
            "Customer ID": r.customer_id,
            "Expected": r.expected_amount,
            "Paid": r.paid_amount if r.paid_amount is not None else "-",
            "Bank Received": r.bank_received_amount if r.bank_received_amount is not None else "-",
            "Transaction ID": r.transaction_id or "-",
            "Bank Txn ID": r.bank_transaction_id or "-",
            "Status": r.status.value,
            "Confidence": r.confidence_score,
            "Discrepancy": r.discrepancy_amount,
            "Explanation": r.explanation
        })

    df = pd.DataFrame(data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reconciliation_results.csv"}
    )

@report_router.get("/exceptions/json", summary="Get Exceptions Ledger (JSON)")
def get_exceptions_json():
    return recon_service.get_exceptions_list()

@report_router.get("/exceptions/csv", summary="Export Exceptions Ledger (CSV)")
def export_exceptions_csv():
    exceptions = recon_service.get_exceptions_list()
    df = pd.DataFrame(exceptions)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=exceptions_ledger.csv"}
    )

@report_router.get("/ai-investigations/json", summary="Get AI Investigations Report (JSON)")
def get_ai_investigations_json():
    return ai_service.investigate_all_exceptions()

@report_router.get("/ai-investigations/csv", summary="Export AI Investigations Report (CSV)")
def export_ai_investigations_csv():
    invs = ai_service.investigate_all_exceptions()
    df = pd.DataFrame(invs)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_investigations_report.csv"}
    )

@report_router.get("/audit/json", summary="Get Audit Trail Report (JSON)")
def get_audit_trail_json():
    return ai_service.get_audit_trail()

@report_router.get("/audit/csv", summary="Export Audit Trail (CSV)")
def export_audit_trail_csv():
    logs = ai_service.get_audit_trail()
    df = pd.DataFrame(logs)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_trail.csv"}
    )

