"""
Deterministic Reconciliation Engine
Executes rule-based matching across Orders, Payments, and Bank Transactions.
Assigns explainable reconciliation statuses and invokes the ConfidenceScorer.
"""

from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from .models import (
    OrderRecord, PaymentRecord, BankRecord,
    ReconciliationResultRecord, ReconciliationStatus
)
from .scorer import ConfidenceScorer, ScoringConfig

class DeterministicMatcher:
    def __init__(self, scorer: Optional[ConfidenceScorer] = None):
        self.scorer = scorer or ConfidenceScorer()

    def reconcile(
        self,
        orders: List[OrderRecord],
        payments: List[PaymentRecord],
        bank_txns: List[BankRecord]
    ) -> List[ReconciliationResultRecord]:
        results: List[ReconciliationResultRecord] = []

        # Index payments by order_id and transaction_id
        payments_by_order: Dict[str, List[PaymentRecord]] = {}
        payments_by_txn_id: Dict[str, List[PaymentRecord]] = {}
        for p in payments:
            if p.order_id:
                payments_by_order.setdefault(p.order_id, []).append(p)
            if p.transaction_id:
                payments_by_txn_id.setdefault(p.transaction_id, []).append(p)

        # Index bank records by reference
        bank_by_ref: Dict[str, BankRecord] = {}
        bank_by_txn_id: Dict[str, BankRecord] = {}
        matched_bank_ids: Set[str] = set()

        for b in bank_txns:
            ref = b.transaction_reference.upper()
            bank_by_ref[ref] = b
            # Extract potential TXN ID from REF-TXNxxxx pattern
            if "TXN" in ref:
                parts = ref.split("-")
                for p in parts:
                    if p.startswith("TXN"):
                        bank_by_txn_id[p] = b

        for order in orders:
            order_id = order.order_id
            order_payments = payments_by_order.get(order_id, [])

            # Check CASE 4: Missing Payment
            if not order_payments:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.MISSING_PAYMENT,
                    expected_amount=order.expected_amount,
                    paid_amount=None,
                    bank_amount=None
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=None,
                    bank_received_amount=None,
                    transaction_id=None,
                    payment_id=None,
                    bank_transaction_id=None,
                    status=ReconciliationStatus.MISSING_PAYMENT,
                    confidence_score=score,
                    discrepancy_amount=order.expected_amount,
                    explanation="No payment record was logged for this customer order.",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None
                ))
                continue

            # Check CASE 5: Duplicate Payment
            payment = order_payments[0]
            is_duplicate = len(order_payments) > 1 or len(payments_by_txn_id.get(payment.transaction_id, [])) > 1

            if is_duplicate:
                # Find bank transaction if present
                bank_rec = bank_by_txn_id.get(payment.transaction_id) or bank_by_ref.get(f"REF-{payment.transaction_id}")
                if bank_rec:
                    matched_bank_ids.add(bank_rec.bank_transaction_id)

                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.DUPLICATE_TRANSACTION,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=bank_rec.received_amount if bank_rec else None,
                    is_duplicate=True
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=bank_rec.received_amount if bank_rec else None,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=bank_rec.bank_transaction_id if bank_rec else None,
                    status=ReconciliationStatus.DUPLICATE_TRANSACTION,
                    confidence_score=score,
                    discrepancy_amount=0.0 if (bank_rec and bank_rec.received_amount == order.expected_amount) else abs(order.expected_amount - (payment.paid_amount or 0.0)),
                    explanation=f"Multiple payment attempts detected for Order {order.order_id} (Txn: {payment.transaction_id}).",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                    bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec and bank_rec.transaction_date else None
                ))
                continue

            # Look up Bank Transaction
            exact_ref = f"REF-{payment.transaction_id}"
            bank_rec = bank_by_ref.get(exact_ref)
            ref_mismatch_detected = False

            if not bank_rec:
                # Search for reference mismatch (e.g. ERR-REF-TXN0099-WRONG or fuzzy txn_id match)
                bank_rec = bank_by_txn_id.get(payment.transaction_id)
                if not bank_rec:
                    for ref_key, b_item in bank_by_ref.items():
                        if payment.transaction_id in ref_key and b_item.bank_transaction_id not in matched_bank_ids:
                            bank_rec = b_item
                            break

                if bank_rec:
                    ref_mismatch_detected = True

            if bank_rec:
                matched_bank_ids.add(bank_rec.bank_transaction_id)

            # Check CASE 3: Missing Bank Transaction
            if not bank_rec:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.MISSING_BANK_TRANSACTION,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=None
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=None,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=None,
                    status=ReconciliationStatus.MISSING_BANK_TRANSACTION,
                    confidence_score=score,
                    discrepancy_amount=order.expected_amount,
                    explanation="Payment gateway transaction exists but no bank settlement credit was recorded.",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None
                ))
                continue

            # Check CASE 7: Reference Mismatch
            if ref_mismatch_detected:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.REFERENCE_MISMATCH,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=bank_rec.received_amount,
                    reference_matched=False
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=bank_rec.received_amount,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=bank_rec.bank_transaction_id,
                    status=ReconciliationStatus.REFERENCE_MISMATCH,
                    confidence_score=score,
                    discrepancy_amount=abs(order.expected_amount - bank_rec.received_amount),
                    explanation=f"Bank reference '{bank_rec.transaction_reference}' contains formatting errors or mismatch.",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                    bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec.transaction_date else None
                ))
                continue

            # Check CASE 8: Partial Payment
            if payment.paid_amount < order.expected_amount:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.PARTIAL_PAYMENT,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=bank_rec.received_amount
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=bank_rec.received_amount,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=bank_rec.bank_transaction_id,
                    status=ReconciliationStatus.PARTIAL_PAYMENT,
                    confidence_score=score,
                    discrepancy_amount=round(order.expected_amount - payment.paid_amount, 2),
                    explanation=f"Paid amount ({payment.paid_amount}) is less than order expected amount ({order.expected_amount}).",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                    bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec.transaction_date else None
                ))
                continue

            # Check CASE 2: Amount Mismatch
            if bank_rec.received_amount != payment.paid_amount or payment.paid_amount != order.expected_amount:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.AMOUNT_MISMATCH,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=bank_rec.received_amount
                )
                diff = abs(payment.paid_amount - bank_rec.received_amount)
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=bank_rec.received_amount,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=bank_rec.bank_transaction_id,
                    status=ReconciliationStatus.AMOUNT_MISMATCH,
                    confidence_score=score,
                    discrepancy_amount=round(diff, 2),
                    explanation=f"Discrepancy detected between paid amount ({payment.paid_amount}) and bank received amount ({bank_rec.received_amount}).",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                    bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec.transaction_date else None
                ))
                continue

            # Check CASE 6: Date Mismatch (>3 days lag)
            days_diff = 0
            if payment.payment_date and bank_rec.transaction_date:
                days_diff = abs((bank_rec.transaction_date - payment.payment_date).days)

            if days_diff > 3:
                score, reasons = self.scorer.calculate_score(
                    status=ReconciliationStatus.DATE_MISMATCH,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_amount=bank_rec.received_amount,
                    days_diff=days_diff
                )
                results.append(ReconciliationResultRecord(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    expected_amount=order.expected_amount,
                    paid_amount=payment.paid_amount,
                    bank_received_amount=bank_rec.received_amount,
                    transaction_id=payment.transaction_id,
                    payment_id=payment.payment_id,
                    bank_transaction_id=bank_rec.bank_transaction_id,
                    status=ReconciliationStatus.DATE_MISMATCH,
                    confidence_score=score,
                    discrepancy_amount=0.0,
                    explanation=f"Settlement lag of {days_diff} days exceeds expected threshold of 3 days.",
                    reasons=reasons,
                    order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                    bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec.transaction_date else None
                ))
                continue

            # CASE 1: Exact MATCHED
            score, reasons = self.scorer.calculate_score(
                status=ReconciliationStatus.MATCHED,
                expected_amount=order.expected_amount,
                paid_amount=payment.paid_amount,
                bank_amount=bank_rec.received_amount
            )
            results.append(ReconciliationResultRecord(
                order_id=order.order_id,
                customer_id=order.customer_id,
                expected_amount=order.expected_amount,
                paid_amount=payment.paid_amount,
                bank_received_amount=bank_rec.received_amount,
                transaction_id=payment.transaction_id,
                payment_id=payment.payment_id,
                bank_transaction_id=bank_rec.bank_transaction_id,
                status=ReconciliationStatus.MATCHED,
                confidence_score=score,
                discrepancy_amount=0.0,
                explanation="Transaction fully matched and verified across order, gateway, and bank settlement.",
                reasons=reasons,
                order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                payment_date=payment.payment_date.strftime("%Y-%m-%d %H:%M:%S") if payment.payment_date else None,
                bank_date=bank_rec.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if bank_rec.transaction_date else None
            ))

        # Capture CASE 9: Unexpected Extra Bank Transactions (no corresponding order/payment)
        for b_item in bank_txns:
            if b_item.bank_transaction_id not in matched_bank_ids:
                results.append(ReconciliationResultRecord(
                    order_id="UNLINKED_BANK_TXN",
                    customer_id="UNKNOWN",
                    expected_amount=0.0,
                    paid_amount=None,
                    bank_received_amount=b_item.received_amount,
                    transaction_id=b_item.transaction_reference,
                    payment_id=None,
                    bank_transaction_id=b_item.bank_transaction_id,
                    status=ReconciliationStatus.UNRESOLVED,
                    confidence_score=10.0,
                    discrepancy_amount=b_item.received_amount,
                    explanation=f"Unlinked bank credit of {b_item.received_amount} with ref '{b_item.transaction_reference}' has no matching order.",
                    reasons=["Unmatched bank credit without order or payment record."],
                    bank_date=b_item.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if b_item.transaction_date else None
                ))

        return results
