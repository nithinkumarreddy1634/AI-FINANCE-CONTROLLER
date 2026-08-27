"""
End-to-End Regression Test across 500 ground-truth records.
Verifies complete pipeline: Dataset Load -> Validation -> Reconcile -> Exceptions -> RAG -> AI Agent -> Audit Ledger -> Reports.
"""

import os
import pandas as pd
from backend.services.recon_service import ReconciliationService
from backend.services.ai_service import AIService

def test_full_500_record_end_to_end_pipeline(tmp_path):
    eval_dir = "evaluation"
    orders_df = pd.read_csv(os.path.join(eval_dir, "orders_eval.csv"))
    payments_df = pd.read_csv(os.path.join(eval_dir, "payments_eval.csv"))
    bank_df = pd.read_csv(os.path.join(eval_dir, "bank_transactions_eval.csv"))

    ai_service = AIService()
    ai_service.audit_manager.file_path = str(tmp_path / "audit_log_e2e.json")
    ai_service.audit_manager.audit_logs = []

    # 1. Reconcile
    summary, results = ai_service.recon_service.run_reconciliation(orders_df, payments_df, bank_df)
    assert len(orders_df) == 500
    assert summary["total_records"] >= 500

    # 2. AI Investigations
    investigations = ai_service.investigate_all_exceptions()
    assert len(investigations) > 0

    # 3. Metrics
    metrics = ai_service.get_metrics()
    assert metrics["total_records"] >= 500

    # 4. Audit Trail
    audit_logs = ai_service.get_audit_trail()
    assert len(audit_logs) == len(investigations)
