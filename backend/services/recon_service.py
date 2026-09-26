"""
Reconciliation Service Layer
Orchestrates data loading, validation, matching, and in-memory cache management.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from reconciliation import (
    DataValidator, DeterministicMatcher, ReconciliationReporter,
    ReconciliationResultRecord, ReconciliationStatus, ValidationError
)

class ReconciliationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReconciliationService, cls).__new__(cls)
            cls._instance.latest_results: List[ReconciliationResultRecord] = []
            cls._instance.latest_summary: Dict[str, Any] = {}
            cls._instance.validation_errors: List[ValidationError] = []
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cls._instance.data_dir = os.path.join(root_dir, "data")
            cls._instance.results_csv_path = os.path.join(cls._instance.data_dir, "reconciliation_results.csv")
            # Run initial reconciliation so metrics and transactions are never empty
            cls._instance.initialize_default_run()
        return cls._instance

    def initialize_default_run(self):
        orders_p = os.path.join(self.data_dir, "orders.csv")
        payments_p = os.path.join(self.data_dir, "payments.csv")
        bank_p = os.path.join(self.data_dir, "bank_transactions.csv")

        if os.path.exists(orders_p) and os.path.exists(payments_p) and os.path.exists(bank_p):
            orders_df = pd.read_csv(orders_p)
            payments_df = pd.read_csv(payments_p)
            bank_df = pd.read_csv(bank_p)
        else:
            from data.generator import generate_synthetic_data
            orders_df, payments_df, bank_df = generate_synthetic_data(num_orders=120)

        self.run_reconciliation(orders_df, payments_df, bank_df)

    def run_reconciliation(
        self,
        orders_df: pd.DataFrame,
        payments_df: pd.DataFrame,
        bank_df: pd.DataFrame
    ) -> Tuple[Dict[str, Any], List[ReconciliationResultRecord]]:

        validator = DataValidator()
        orders, _ = validator.validate_and_normalize_orders(orders_df)
        payments, _ = validator.validate_and_normalize_payments(payments_df)
        bank_txns, val_errs = validator.validate_and_normalize_bank_txns(bank_df)

        self.validation_errors = val_errs

        matcher = DeterministicMatcher()
        results = matcher.reconcile(orders, payments, bank_txns)

        summary = ReconciliationReporter.generate_summary(results)
        ReconciliationReporter.export_results_csv(results, self.results_csv_path)

        self.latest_results = results
        self.latest_summary = summary

        return summary, results

    def get_summary(self) -> Dict[str, Any]:
        if not self.latest_summary:
            self.initialize_default_run()
        return self.latest_summary

    def get_transactions(
        self,
        status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        if not self.latest_results:
            self.initialize_default_run()

        filtered = self.latest_results

        if status:
            status_clean = status.upper().strip()
            filtered = [r for r in filtered if r.status.value == status_clean]

        if min_confidence is not None:
            filtered = [r for r in filtered if r.confidence_score >= min_confidence]

        if search:
            q = search.lower().strip()
            filtered = [
                r for r in filtered if
                q in r.order_id.lower() or
                q in r.customer_id.lower() or
                (r.transaction_id and q in r.transaction_id.lower()) or
                (r.bank_transaction_id and q in r.bank_transaction_id.lower())
            ]

        return [self._result_to_dict(r) for r in filtered]

    def get_exceptions(self) -> List[Dict[str, Any]]:
        return self.get_exceptions_list()

    def get_exceptions_list(self) -> List[Dict[str, Any]]:
        if not self.latest_results:
            self.initialize_default_run()
        exceptions = [r for r in self.latest_results if r.status != ReconciliationStatus.MATCHED]
        return [self._result_to_dict(r) for r in exceptions]

    def _result_to_dict(self, r: ReconciliationResultRecord) -> Dict[str, Any]:
        return {
            "order_id": r.order_id,
            "customer_id": r.customer_id,
            "expected_amount": r.expected_amount,
            "paid_amount": r.paid_amount,
            "bank_received_amount": r.bank_received_amount,
            "transaction_id": r.transaction_id,
            "payment_id": r.payment_id,
            "bank_transaction_id": r.bank_transaction_id,
            "status": r.status.value,
            "confidence_score": r.confidence_score,
            "discrepancy_amount": r.discrepancy_amount,
            "explanation": r.explanation,
            "reasons": r.reasons,
            "order_date": r.order_date,
            "payment_date": r.payment_date,
            "bank_date": r.bank_date
        }
