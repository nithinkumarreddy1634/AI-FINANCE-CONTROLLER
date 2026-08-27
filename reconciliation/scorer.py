"""
Rule-Based Confidence Scorer
Provides a configurable, explainable confidence score (0-100) for reconciliation decisions.
"""

from typing import Tuple, List, Dict
from dataclasses import dataclass
from .models import ReconciliationStatus

@dataclass
class ScoringConfig:
    matched_base: float = 100.0
    reference_mismatch_penalty: float = 25.0
    date_mismatch_penalty: float = 20.0
    amount_mismatch_minor_penalty: float = 25.0  # < 5% diff
    amount_mismatch_major_penalty: float = 50.0  # >= 5% diff
    partial_payment_penalty: float = 30.0
    duplicate_transaction_penalty: float = 60.0
    missing_bank_penalty: float = 80.0
    missing_payment_penalty: float = 85.0
    unresolved_penalty: float = 90.0

class ConfidenceScorer:
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()

    def calculate_score(
        self,
        status: ReconciliationStatus,
        expected_amount: float,
        paid_amount: Optional[float],
        bank_amount: Optional[float],
        days_diff: Optional[int] = None,
        reference_matched: bool = True,
        is_duplicate: bool = False
    ) -> Tuple[float, List[str]]:
        score = 100.0
        reasons: List[str] = []

        if status == ReconciliationStatus.MATCHED:
            reasons.append("Exact match across order, payment, and bank settlement records.")
            return round(score, 1), reasons

        if is_duplicate or status == ReconciliationStatus.DUPLICATE_TRANSACTION:
            score -= self.config.duplicate_transaction_penalty
            reasons.append("Duplicate transaction ID detected.")

        if status == ReconciliationStatus.MISSING_PAYMENT:
            score -= self.config.missing_payment_penalty
            reasons.append("No payment gateway record found for this order.")

        elif status == ReconciliationStatus.MISSING_BANK_TRANSACTION:
            score -= self.config.missing_bank_penalty
            reasons.append("Payment completed but bank settlement record is missing.")

        elif status == ReconciliationStatus.PARTIAL_PAYMENT:
            score -= self.config.partial_payment_penalty
            if paid_amount and expected_amount:
                pct = round((paid_amount / expected_amount) * 100, 1)
                reasons.append(f"Partial payment received: {pct}% of expected amount.")

        elif status == ReconciliationStatus.AMOUNT_MISMATCH:
            if bank_amount is not None and paid_amount is not None:
                diff = abs(paid_amount - bank_amount)
                rel_diff = diff / max(expected_amount, 1.0)
                if rel_diff >= 0.05:
                    score -= self.config.amount_mismatch_major_penalty
                    reasons.append(f"Major amount mismatch: Received amount differs by {diff:.2f}.")
                else:
                    score -= self.config.amount_mismatch_minor_penalty
                    reasons.append(f"Minor amount mismatch (e.g., fee deduction): Difference is {diff:.2f}.")

        elif status == ReconciliationStatus.DATE_MISMATCH:
            score -= self.config.date_mismatch_penalty
            if days_diff:
                reasons.append(f"Date difference of {days_diff} days between payment and bank settlement exceeds threshold.")

        elif status == ReconciliationStatus.REFERENCE_MISMATCH:
            score -= self.config.reference_mismatch_penalty
            reasons.append("Bank transaction reference format does not cleanly match expected transaction ID pattern.")

        elif status == ReconciliationStatus.UNRESOLVED:
            score -= self.config.unresolved_penalty
            reasons.append("Complex multi-field discrepancy could not be deterministically resolved.")

        # Additional adjustments
        if not reference_matched and status not in [ReconciliationStatus.REFERENCE_MISMATCH, ReconciliationStatus.MISSING_BANK_TRANSACTION]:
            score -= 15.0
            reasons.append("Transaction reference string variance.")

        # Clamp score to [0.0, 100.0]
        final_score = max(0.0, min(100.0, score))
        return round(final_score, 1), reasons

