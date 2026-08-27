"""
Unit tests for Audit Log Manager and human review actions.
"""

from reconciliation.models import ReconciliationResultRecord, ReconciliationStatus
from ai_agent import (
    AuditLogManager, AIDecisionOutput, AIDecisionEnum, AIActionEnum,
    HumanReviewInput, HumanDecisionEnum
)

def test_audit_log_and_human_review(tmp_path):
    log_file = str(tmp_path / "audit_log.json")
    audit_mgr = AuditLogManager(file_path=log_file)

    rule_rec = ReconciliationResultRecord(
        order_id="ORD_AUDIT_1", customer_id="CUST1", expected_amount=1000.0,
        paid_amount=1000.0, bank_received_amount=900.0, transaction_id="TXN1",
        payment_id="PAY1", bank_transaction_id="BNK1", status=ReconciliationStatus.AMOUNT_MISMATCH,
        confidence_score=75.0, discrepancy_amount=100.0, explanation="Fee difference"
    )

    ai_out = AIDecisionOutput(
        order_id="ORD_AUDIT_1", decision=AIDecisionEnum.AMOUNT_MISMATCH, confidence=82.0,
        reason="Commission fee deduction", evidence=["Paid 1000", "Bank 900"], discrepancies=["Diff 100"],
        recommended_action=AIActionEnum.MARK_FOR_REVIEW, requires_human_review=True,
        investigation_id="AI-TEST01", timestamp="2026-08-27 12:00:00"
    )

    audit_entry = audit_mgr.log_investigation(rule_rec, ai_out)
    assert audit_entry.investigation_id == "AI-TEST01"
    assert audit_entry.human_decision is None

    # Perform Human Review Action
    review_in = HumanReviewInput(
        reviewer_name="Senior Auditor",
        decision=HumanDecisionEnum.APPROVED,
        reviewer_note="Verified against gateway fee schedule."
    )

    updated = audit_mgr.record_human_review("AI-TEST01", review_in)
    assert updated is not None
    assert updated.human_decision == "APPROVED"
    assert updated.reviewer_name == "Senior Auditor"
    assert updated.reviewer_note == "Verified against gateway fee schedule."

