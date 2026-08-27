"""
Phase 3 End-to-End Integration Test
Verifies 5 Phase 3 demo scenarios, RAG policy retrieval, controlled tools execution,
candidate ranking, investigation timeline, and 3-way comparative benchmark.
"""

import os
import pandas as pd
from data.demo_scenarios_p3 import generate_phase3_demo_scenarios
from data.generator import generate_synthetic_data
from backend.services.recon_service import ReconciliationService
from backend.services.ai_service import AIService
from ai_agent import (
    AIFinanceControllerAgent, AIEvaluator, AIDecisionEnum, AIActionEnum
)
from reconciliation.models import BankRecord, ReconciliationResultRecord, ReconciliationStatus

def test_phase3_demo_scenarios_pipeline(tmp_path):
    demo_dir = str(tmp_path / "demo_p3_data")
    generate_phase3_demo_scenarios(output_dir=demo_dir)

    orders_df = pd.read_csv(os.path.join(demo_dir, "orders.csv"))
    payments_df = pd.read_csv(os.path.join(demo_dir, "payments.csv"))
    bank_df = pd.read_csv(os.path.join(demo_dir, "bank_transactions.csv"))

    recon_service = ReconciliationService()
    summary, results = recon_service.run_reconciliation(orders_df, payments_df, bank_df)

    agent = AIFinanceControllerAgent()

    # Demo 1: Settlement Date Difference
    rec_d1 = next(r for r in results if r.order_id == "P3_DEMO_01_DATE")
    out_d1, state_d1 = agent.investigate_exception(rec_d1)
    assert len(state_d1.policy_citations) > 0
    assert any("Settlement" in c["citation_label"] for c in state_d1.policy_citations)

    # Demo 2: Partial Payment
    rec_d2 = next(r for r in results if r.order_id == "P3_DEMO_02_PARTIAL")
    out_d2, state_d2 = agent.investigate_exception(rec_d2)
    assert out_d2.decision == AIDecisionEnum.PARTIAL_MATCH
    assert out_d2.recommended_action == AIActionEnum.MARK_FOR_REVIEW

    # Demo 3: Candidate Ranking
    rec_d3 = next(r for r in results if r.order_id == "P3_DEMO_03_CANDIDATES")
    candidates = [
        BankRecord("BNK_P3_3A", "REF-TXN_P3_3", None, 3500.0, "SETTLED"),
        BankRecord("BNK_P3_3B", "REF-TXN_P3_3_ALT", None, 3000.0, "SETTLED")
    ]
    out_d3, state_d3 = agent.investigate_exception(rec_d3, bank_candidates=candidates)
    assert len(state_d3.candidate_comparisons) == 2
    assert state_d3.candidate_comparisons[0]["bank_transaction_id"] == "BNK_P3_3A"

    # Demo 4: Missing Evidence
    rec_d4 = next(r for r in results if r.order_id == "P3_DEMO_04_NOEVIDENCE")
    out_d4, state_d4 = agent.investigate_exception(rec_d4)
    assert "INSUFFICIENT_EVIDENCE" in out_d4.reason
    assert out_d4.recommended_action == AIActionEnum.ESCALATE

    # Demo 5: AI Hallucination Protection
    rec_d5 = next(r for r in results if r.order_id == "P3_DEMO_05_HALLUCINATION")
    out_d5, state_d5 = agent.investigate_exception(rec_d5)
    # Received amount 3800 vs expected 4200 -> post-LLM rule validator must prevent auto reconcile
    assert out_d5.recommended_action == AIActionEnum.MARK_FOR_REVIEW
    assert out_d5.requires_human_review is True

def test_full_phase3_agentic_pipeline(tmp_path):
    out_dir = str(tmp_path / "synthetic_data_p3")
    generate_synthetic_data(output_dir=out_dir, num_records=120, seed=42)

    orders_df = pd.read_csv(os.path.join(out_dir, "orders.csv"))
    payments_df = pd.read_csv(os.path.join(out_dir, "payments.csv"))
    bank_df = pd.read_csv(os.path.join(out_dir, "bank_transactions.csv"))

    ai_service = AIService()
    ai_service.audit_manager.file_path = str(tmp_path / "audit_log_p3.json")
    ai_service.recon_service.run_reconciliation(orders_df, payments_df, bank_df)

    investigations = ai_service.investigate_all_exceptions()
    assert len(investigations) > 0

    metrics = ai_service.get_metrics()
    assert "three_way_comparison_table" in metrics
    assert len(metrics["three_way_comparison_table"]) >= 4

    # Verify timeline tracking for a sample investigation
    sample_order_id = investigations[0]["order_id"]
    state = ai_service.agent.states_cache.get(sample_order_id)
    assert state is not None
    assert len(state.timeline) >= 4
    assert state.policies_retrieved is True

