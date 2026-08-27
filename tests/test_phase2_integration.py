"""
Phase 2 End-to-End Integration Test
Verifies demo scenarios, AI exception investigations, audit logging, and comparative metrics.
"""

import os
import pandas as pd
from data.demo_scenarios import generate_demo_scenarios
from data.generator import generate_synthetic_data
from backend.services.recon_service import ReconciliationService
from backend.services.ai_service import AIService
from ai_agent import (
    AIFinanceControllerAgent, AIEvaluator, AIDecisionEnum, AIActionEnum
)

def test_demo_scenarios_pipeline(tmp_path):
    demo_dir = str(tmp_path / "demo_data")
    generate_demo_scenarios(output_dir=demo_dir)

    orders_df = pd.read_csv(os.path.join(demo_dir, "orders.csv"))
    payments_df = pd.read_csv(os.path.join(demo_dir, "payments.csv"))
    bank_df = pd.read_csv(os.path.join(demo_dir, "bank_transactions.csv"))

    recon_service = ReconciliationService()
    summary, results = recon_service.run_reconciliation(orders_df, payments_df, bank_df)

    agent = AIFinanceControllerAgent()
    investigations = agent.batch_investigate(results)

    # 1. Exact match order (SCENARIO_01_EXACT) should be filtered out from exception investigations
    investigated_ids = [inv.order_id for inv in investigations]
    assert "SCENARIO_01_EXACT" not in investigated_ids

    # 2. Scenario 2: Partial payment
    partial_inv = next(inv for inv in investigations if inv.order_id == "SCENARIO_02_PARTIAL")
    assert partial_inv.decision == AIDecisionEnum.PARTIAL_MATCH
    assert partial_inv.recommended_action == AIActionEnum.MARK_FOR_REVIEW

    # 3. Scenario 3: Reference difference
    ref_inv = next(inv for inv in investigations if inv.order_id == "ORD-1042")
    assert ref_inv.decision == AIDecisionEnum.LIKELY_MATCH
    assert ref_inv.recommended_action == AIActionEnum.MARK_FOR_REVIEW

    # 4. Scenario 4: Missing bank transaction
    nobank_inv = next(inv for inv in investigations if inv.order_id == "SCENARIO_04_NOBANK")
    assert nobank_inv.decision == AIDecisionEnum.MISSING_BANK_TRANSACTION
    assert nobank_inv.recommended_action == AIActionEnum.ESCALATE

    # 5. Scenario 5: Duplicate transaction
    dup_inv = next(inv for inv in investigations if inv.order_id == "SCENARIO_05_DUP")
    assert dup_inv.decision == AIDecisionEnum.DUPLICATE

    # 6. Scenario 6: Insufficient evidence
    missing_inv = next(inv for inv in investigations if inv.order_id == "SCENARIO_06_MISSING")
    assert missing_inv.decision == AIDecisionEnum.MISSING_PAYMENT or missing_inv.decision == AIDecisionEnum.UNRESOLVED
    assert missing_inv.requires_human_review is True

def test_full_phase2_metrics_and_audit(tmp_path):
    out_dir = str(tmp_path / "synthetic_data")
    generate_synthetic_data(output_dir=out_dir, num_records=120, seed=42)

    orders_df = pd.read_csv(os.path.join(out_dir, "orders.csv"))
    payments_df = pd.read_csv(os.path.join(out_dir, "payments.csv"))
    bank_df = pd.read_csv(os.path.join(out_dir, "bank_transactions.csv"))

    ai_service = AIService()
    ai_service.audit_manager.file_path = str(tmp_path / "audit_log.json")
    ai_service.audit_manager.audit_logs = []
    ai_service.recon_service.run_reconciliation(orders_df, payments_df, bank_df)

    investigations = ai_service.investigate_all_exceptions()
    assert len(investigations) > 0

    metrics = ai_service.get_metrics()
    assert "baseline_match_rate_pct" in metrics
    assert "ai_resolution_rate_pct" in metrics
    assert "overall_accuracy_pct" in metrics
    assert "comparison_table" in metrics

    # Audit trail verification
    audit_logs = ai_service.get_audit_trail()
    assert len(audit_logs) == len(investigations)

