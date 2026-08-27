"""
Reconciliation Report & Analytics Generator
Calculates summary statistics and exports detailed reconciliation_results.csv.
"""

from typing import List, Dict, Any
import pandas as pd
from .models import ReconciliationResultRecord, ReconciliationStatus

class ReconciliationReporter:
    @staticmethod
    def generate_summary(results: List[ReconciliationResultRecord]) -> Dict[str, Any]:
        total_records = len(results)
        matched_count = sum(1 for r in results if r.status == ReconciliationStatus.MATCHED)
        unmatched_count = total_records - matched_count
        exception_count = unmatched_count

        match_rate = round((matched_count / total_records * 100), 2) if total_records > 0 else 0.0

        total_expected = sum(r.expected_amount for r in results if r.expected_amount)
        total_received = sum(r.bank_received_amount for r in results if r.bank_received_amount is not None)
        total_discrepancy = sum(r.discrepancy_amount for r in results)

        duplicates_count = sum(1 for r in results if r.status == ReconciliationStatus.DUPLICATE_TRANSACTION)
        missing_payments_count = sum(1 for r in results if r.status == ReconciliationStatus.MISSING_PAYMENT)
        missing_bank_count = sum(1 for r in results if r.status == ReconciliationStatus.MISSING_BANK_TRANSACTION)
        missing_txns_count = missing_payments_count + missing_bank_count
        amount_mismatches_count = sum(1 for r in results if r.status == ReconciliationStatus.AMOUNT_MISMATCH)
        date_mismatches_count = sum(1 for r in results if r.status == ReconciliationStatus.DATE_MISMATCH)
        ref_mismatches_count = sum(1 for r in results if r.status == ReconciliationStatus.REFERENCE_MISMATCH)
        partial_payments_count = sum(1 for r in results if r.status == ReconciliationStatus.PARTIAL_PAYMENT)
        unresolved_count = sum(1 for r in results if r.status == ReconciliationStatus.UNRESOLVED)

        status_breakdown = {
            ReconciliationStatus.MATCHED.value: matched_count,
            ReconciliationStatus.AMOUNT_MISMATCH.value: amount_mismatches_count,
            ReconciliationStatus.MISSING_PAYMENT.value: missing_payments_count,
            ReconciliationStatus.MISSING_BANK_TRANSACTION.value: missing_bank_count,
            ReconciliationStatus.DUPLICATE_TRANSACTION.value: duplicates_count,
            ReconciliationStatus.DATE_MISMATCH.value: date_mismatches_count,
            ReconciliationStatus.REFERENCE_MISMATCH.value: ref_mismatches_count,
            ReconciliationStatus.PARTIAL_PAYMENT.value: partial_payments_count,
            ReconciliationStatus.UNRESOLVED.value: unresolved_count
        }

        return {
            "total_records": total_records,
            "matched_records": matched_count,
            "unmatched_records": unmatched_count,
            "exception_records": exception_count,
            "match_rate_pct": match_rate,
            "total_expected_amount": round(total_expected, 2),
            "total_received_amount": round(total_received, 2),
            "total_discrepancy_amount": round(total_discrepancy, 2),
            "duplicates_count": duplicates_count,
            "missing_transactions_count": missing_txns_count,
            "amount_mismatches_count": amount_mismatches_count,
            "status_breakdown": status_breakdown
        }

    @staticmethod
    def export_results_csv(results: List[ReconciliationResultRecord], output_filepath: str) -> str:
        data = []
        for r in results:
            data.append({
                "Order ID": r.order_id,
                "Customer ID": r.customer_id,
                "Expected": r.expected_amount,
                "Paid": r.paid_amount if r.paid_amount is not None else "-",
                "Bank Received": r.bank_received_amount if r.bank_received_amount is not None else "-",
                "Transaction ID": r.transaction_id if r.transaction_id else "-",
                "Bank Txn ID": r.bank_transaction_id if r.bank_transaction_id else "-",
                "Status": r.status.value,
                "Confidence": r.confidence_score,
                "Discrepancy": r.discrepancy_amount,
                "Explanation": r.explanation,
                "Order Date": r.order_date or "-",
                "Payment Date": r.payment_date or "-",
                "Bank Date": r.bank_date or "-"
            })

        df = pd.DataFrame(data)
        df.to_csv(output_filepath, index=False)
        return output_filepath

