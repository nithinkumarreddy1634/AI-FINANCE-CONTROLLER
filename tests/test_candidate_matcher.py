"""
Unit tests for Multi-Signal Candidate Matcher Engine.
"""

from datetime import datetime
from reconciliation.models import PaymentRecord, BankRecord
from ai_agent.candidate_matcher import CandidateMatcher

def test_candidate_matcher_scoring_and_ranking():
    payment = PaymentRecord(
        payment_id="PAY100", order_id="ORD100", transaction_id="TXN100",
        payment_date=datetime(2026, 2, 10, 10, 0, 0), paid_amount=3500.0,
        payment_status="SUCCESS", payment_method="UPI"
    )

    candidate_a = BankRecord(
        bank_transaction_id="BNK100_A", transaction_reference="REF-TXN100",
        transaction_date=datetime(2026, 2, 11, 10, 0, 0), received_amount=3500.0,
        bank_status="SETTLED"
    )

    candidate_b = BankRecord(
        bank_transaction_id="BNK100_B", transaction_reference="REF-TXN100-ALT",
        transaction_date=datetime(2026, 2, 18, 10, 0, 0), received_amount=3000.0,
        bank_status="SETTLED"
    )

    ranked = CandidateMatcher.rank_candidates(payment, [candidate_b, candidate_a], expected_amount=3500.0)

    assert len(ranked) == 2
    # Candidate A should be ranked #1
    assert ranked[0].bank_record.bank_transaction_id == "BNK100_A"
    assert ranked[0].candidate_score > ranked[1].candidate_score
    assert ranked[0].identifier_score == 100.0

