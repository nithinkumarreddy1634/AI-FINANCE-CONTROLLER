"""
Unit tests for AI Agent evidence compilation and provider outputs.
"""

from reconciliation.models import ReconciliationResultRecord, ReconciliationStatus
from ai_agent import (
    AIFinanceControllerAgent, MockAIProvider, EvidencePackage,
    AIDecisionEnum, AIActionEnum
)

def test_evidence_package_builder():
    agent = AIFinanceControllerAgent()
    record = ReconciliationResultRecord(
        order_id="ORD100",
        customer_id="CUST1",
        expected_amount=5000.0,
        paid_amount=5000.0,
        bank_received_amount=4500.0,
        transaction_id="TXN100",
        payment_id="PAY100",
        bank_transaction_id="BNK100",
        status=ReconciliationStatus.PARTIAL_PAYMENT,
        confidence_score=70.0,
        discrepancy_amount=500.0,
        explanation="Shortfall detected",
        reasons=["Paid amount less than expected"]
    )

    evidence = agent.build_evidence_package(record)
    assert evidence.order_id == "ORD100"
    assert evidence.expected_amount == 5000.0
    assert evidence.received_amount == 4500.0
    assert evidence.phase1_status == "PARTIAL_PAYMENT"

def test_mock_provider_partial_payment():
    provider = MockAIProvider()
    evidence = EvidencePackage(
        order_id="ORD101",
        expected_amount=5000.0,
        paid_amount=5000.0,
        received_amount=4500.0,
        phase1_status="PARTIAL_PAYMENT"
    )

    output = provider.investigate(evidence)
    assert output.decision == AIDecisionEnum.PARTIAL_MATCH
    assert output.confidence >= 90.0
    assert output.recommended_action == AIActionEnum.MARK_FOR_REVIEW
    assert output.requires_human_review is True

def test_mock_provider_insufficient_evidence():
    provider = MockAIProvider()
    evidence = EvidencePackage(
        order_id="UNLINKED_BANK_TXN",
        expected_amount=0.0,
        paid_amount=None,
        received_amount=None,
        phase1_status="UNRESOLVED"
    )

    output = provider.investigate(evidence)
    assert "INSUFFICIENT_EVIDENCE" in output.reason
    assert output.decision == AIDecisionEnum.UNRESOLVED
    assert output.recommended_action == AIActionEnum.ESCALATE
    assert output.requires_human_review is True

