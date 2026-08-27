"""
Mock AI Provider
Deterministic, zero-token AI Provider for testing, demo scenarios, and offline fallback.
Simulates deep evidence-backed financial reasoning over Evidence Packages.
"""

from datetime import datetime
import uuid
from typing import List
from ai_agent.models import (
    EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
)
from ai_agent.providers.base import AIProvider

class MockAIProvider(AIProvider):
    def investigate(self, evidence: EvidencePackage) -> AIDecisionOutput:
        investigation_id = f"AI-{uuid.uuid4().hex[:6].upper()}"
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Check Insufficient Evidence
        if not evidence.order_id or evidence.order_id == "UNLINKED_BANK_TXN" or (evidence.paid_amount is None and evidence.received_amount is None):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.UNRESOLVED,
                confidence=15.0,
                reason="INSUFFICIENT_EVIDENCE: Essential financial fields or order bindings are missing from records.",
                evidence=["Unlinked transaction without valid order mapping"],
                discrepancies=["Missing order linkage", "Missing payment gateway log"],
                recommended_action=AIActionEnum.ESCALATE,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 2. Check Missing Payment
        if evidence.phase1_status == "MISSING_PAYMENT" or (evidence.paid_amount is None and evidence.received_amount is None):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.MISSING_PAYMENT,
                confidence=25.0,
                reason="Order was created in system, but no payment gateway log or bank credit was recorded.",
                evidence=[f"Order expected amount: ₹{evidence.expected_amount}"],
                discrepancies=["No gateway payment record logged"],
                recommended_action=AIActionEnum.ESCALATE,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 3. Check Missing Bank Transaction
        if evidence.phase1_status == "MISSING_BANK_TRANSACTION" or (evidence.paid_amount is not None and evidence.received_amount is None):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.MISSING_BANK_TRANSACTION,
                confidence=30.0,
                reason="Payment gateway transaction succeeded, but corresponding bank settlement record is absent.",
                evidence=[
                    f"Payment ID {evidence.payment_id} recorded paid amount ₹{evidence.paid_amount}",
                    "No bank statement credit reference matches this transaction"
                ],
                discrepancies=["Unsettled payment gateway transaction"],
                recommended_action=AIActionEnum.ESCALATE,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 4. Check Partial Match / Partial Payment
        if evidence.phase1_status == "PARTIAL_PAYMENT" or (
            evidence.expected_amount and evidence.received_amount and evidence.received_amount < evidence.expected_amount
        ):
            diff = round((evidence.expected_amount or 0.0) - (evidence.received_amount or 0.0), 2)
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.PARTIAL_MATCH,
                confidence=91.0,
                reason=f"The payment record matches the order, but the bank settlement contains only ₹{evidence.received_amount}. The ₹{diff} difference prevents full automatic reconciliation.",
                evidence=[
                    f"Order ID {evidence.order_id} expected ₹{evidence.expected_amount}",
                    f"Bank received amount ₹{evidence.received_amount}",
                    f"Discrepancy variance: ₹{diff}"
                ],
                discrepancies=[f"Shortfall of ₹{diff} in bank settlement"],
                recommended_action=AIActionEnum.MARK_FOR_REVIEW,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 5. Check Duplicate Transaction
        if evidence.phase1_status == "DUPLICATE_TRANSACTION" or (evidence.order_id and "DUP" in evidence.order_id):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.DUPLICATE,
                confidence=75.0,
                reason=f"Multiple payment webhooks or bank settlements detected for transaction ID {evidence.transaction_id}.",
                evidence=[
                    f"Duplicate logs detected for Order {evidence.order_id}",
                    f"Transaction ID {evidence.transaction_id}"
                ],
                discrepancies=["Potential double payment attempt"],
                recommended_action=AIActionEnum.MARK_FOR_REVIEW,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 6. Check Reference Mismatch
        if evidence.phase1_status == "REFERENCE_MISMATCH" or (
            evidence.transaction_reference and ("TYPO" in evidence.transaction_reference or "ALT" in evidence.transaction_reference)
        ) or (
            evidence.order_id and ("TYPO" in evidence.order_id or "REF" in evidence.order_id or "REFERENCE" in evidence.order_id)
        ):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.LIKELY_MATCH,
                confidence=85.0,
                reason=f"Bank reference has formatting variations but contains matching transaction identifier.",
                evidence=[
                    f"Order ID {evidence.order_id} corresponds to transaction {evidence.transaction_id}",
                    f"Amounts match exactly (₹{evidence.expected_amount})"
                ],
                discrepancies=["Non-standard bank reference format"],
                recommended_action=AIActionEnum.MARK_FOR_REVIEW,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 7. Check Amount Mismatch
        if evidence.phase1_status == "AMOUNT_MISMATCH":
            paid = evidence.paid_amount or 0.0
            rec = evidence.received_amount or 0.0
            diff = round(abs(paid - rec), 2)
            pct = round((diff / max(paid, 1.0)) * 100, 1)
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.AMOUNT_MISMATCH,
                confidence=82.0,
                reason=f"Identified {pct}% variance (₹{diff}) between gateway paid amount (₹{paid}) and bank received amount (₹{rec}).",
                evidence=[
                    f"Paid amount: ₹{paid}",
                    f"Bank settlement received: ₹{rec}",
                    f"Deduction difference: ₹{diff} ({pct}%)"
                ],
                discrepancies=[f"Amount variance of ₹{diff}"],
                recommended_action=AIActionEnum.MARK_FOR_REVIEW,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 8. Check Date Mismatch
        if evidence.phase1_status == "DATE_MISMATCH" or (
            evidence.order_id and ("DATE" in evidence.order_id or "LAG" in evidence.order_id)
        ):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.DATE_MISMATCH,
                confidence=88.0,
                reason=f"Transaction amounts (₹{evidence.expected_amount}) match, but settlement date lag exceeds standard threshold.",
                evidence=[
                    f"Amounts match: ₹{evidence.expected_amount}",
                    f"Payment date: {evidence.payment_date}",
                    f"Bank date: {evidence.transaction_date}"
                ],
                discrepancies=["Settlement date lag > 2 days"],
                recommended_action=AIActionEnum.MARK_FOR_REVIEW,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 9. Check Multiple Candidates
        if evidence.order_id and "CANDIDATE" in evidence.order_id:
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.UNRESOLVED,
                confidence=50.0,
                reason=f"Multiple candidate bank settlements found for Order {evidence.order_id}.",
                evidence=["Multiple candidate bank records ranked"],
                discrepancies=["Ambiguous candidate bank settlements"],
                recommended_action=AIActionEnum.ESCALATE,
                requires_human_review=True,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # 10. Check Exact Match / Matched
        if evidence.phase1_status in ["MATCHED", "EXACT_MATCH"] or (
            evidence.expected_amount is not None and evidence.paid_amount is not None and evidence.received_amount is not None and
            abs(evidence.expected_amount - evidence.paid_amount) < 0.01 and
            abs(evidence.paid_amount - evidence.received_amount) < 0.01
        ):
            return AIDecisionOutput(
                order_id=evidence.order_id,
                decision=AIDecisionEnum.LIKELY_MATCH,
                confidence=98.0,
                reason=f"Order {evidence.order_id}, gateway payment, and bank settlement match exactly (₹{evidence.expected_amount}).",
                evidence=[
                    f"Order ID {evidence.order_id} expected ₹{evidence.expected_amount}",
                    f"Payment paid ₹{evidence.paid_amount}",
                    f"Bank received ₹{evidence.received_amount}"
                ],
                discrepancies=[],
                recommended_action=AIActionEnum.AUTO_RECONCILE,
                requires_human_review=False,
                investigation_id=investigation_id,
                timestamp=ts
            )

        # Default Fallback for ambiguous cases
        return AIDecisionOutput(
            order_id=evidence.order_id,
            decision=AIDecisionEnum.UNRESOLVED,
            confidence=45.0,
            reason=f"Complex financial variance for Order {evidence.order_id} could not be automatically reconciled without human review.",
            evidence=[f"Phase 1 status: {evidence.phase1_status}"],
            discrepancies=evidence.detected_discrepancies or ["Unclassified discrepancy"],
            recommended_action=AIActionEnum.ESCALATE,
            requires_human_review=True,
            investigation_id=investigation_id,
            timestamp=ts
        )
