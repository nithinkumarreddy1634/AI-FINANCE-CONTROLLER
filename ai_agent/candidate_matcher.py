"""
Multi-Signal Candidate Matcher Engine
Evaluates multiple possible bank transaction candidates using identifier, text,
amount, and temporal similarity signals. Normalizes candidate scores (0-100) and ranks them.
"""

import difflib
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from reconciliation.models import PaymentRecord, BankRecord

class CandidateMatchResult:
    def __init__(
        self,
        bank_record: BankRecord,
        candidate_score: float,
        identifier_score: float,
        amount_score: float,
        temporal_score: float,
        text_score: float,
        explanation: str
    ):
        self.bank_record = bank_record
        self.candidate_score = round(candidate_score, 1)
        self.identifier_score = round(identifier_score, 1)
        self.amount_score = round(amount_score, 1)
        self.temporal_score = round(temporal_score, 1)
        self.text_score = round(text_score, 1)
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bank_transaction_id": self.bank_record.bank_transaction_id,
            "transaction_reference": self.bank_record.transaction_reference,
            "received_amount": self.bank_record.received_amount,
            "bank_date": self.bank_record.transaction_date.strftime("%Y-%m-%d") if self.bank_record.transaction_date else None,
            "candidate_score": self.candidate_score,
            "identifier_score": self.identifier_score,
            "amount_score": self.amount_score,
            "temporal_score": self.temporal_score,
            "text_score": self.text_score,
            "explanation": self.explanation
        }

class CandidateMatcher:
    @staticmethod
    def calculate_candidate_score(
        payment: PaymentRecord,
        bank_rec: BankRecord,
        expected_amount: float
    ) -> CandidateMatchResult:

        # 1. Identifier Similarity (0-100)
        id_score = 0.0
        ref_upper = bank_rec.transaction_reference.upper()
        txn_id_upper = payment.transaction_id.upper()
        order_id_upper = payment.order_id.upper()

        if f"REF-{txn_id_upper}" == ref_upper:
            id_score = 100.0
        elif txn_id_upper in ref_upper or order_id_upper in ref_upper:
            id_score = 80.0
        elif difflib.SequenceMatcher(None, txn_id_upper, ref_upper).ratio() > 0.6:
            id_score = 60.0
        else:
            id_score = 10.0

        # 2. Text Similarity (0-100)
        text_score = round(difflib.SequenceMatcher(None, txn_id_upper, ref_upper).ratio() * 100, 1)

        # 3. Amount Similarity (0-100)
        diff = abs(expected_amount - bank_rec.received_amount)
        rel_diff_pct = (diff / max(expected_amount, 1.0)) * 100
        amount_score = max(0.0, 100.0 - rel_diff_pct)

        # 4. Temporal Similarity (0-100)
        days_diff = 0
        if payment.payment_date and bank_rec.transaction_date:
            days_diff = abs((bank_rec.transaction_date - payment.payment_date).days)
        temporal_score = max(0.0, 100.0 - (days_diff * 15.0))

        # Combined Weighted Score
        candidate_score = (id_score * 0.40) + (amount_score * 0.35) + (temporal_score * 0.15) + (text_score * 0.10)

        explanation = f"Match Score: {candidate_score:.1f}/100 (ID: {id_score:.0f}, Amount: {amount_score:.0f}, Temporal: {temporal_score:.0f})"

        return CandidateMatchResult(
            bank_record=bank_rec,
            candidate_score=candidate_score,
            identifier_score=id_score,
            amount_score=amount_score,
            temporal_score=temporal_score,
            text_score=text_score,
            explanation=explanation
        )

    @classmethod
    def rank_candidates(
        cls,
        payment: PaymentRecord,
        bank_candidates: List[BankRecord],
        expected_amount: float
    ) -> List[CandidateMatchResult]:

        results = [
            cls.calculate_candidate_score(payment, b, expected_amount)
            for b in bank_candidates
        ]
        results.sort(key=lambda x: x.candidate_score, reverse=True)
        return results

