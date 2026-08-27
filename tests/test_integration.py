"""
Integration Test: Processes full synthetic dataset through validator, matcher, reporter, and API service.
"""

import os
import pandas as pd
from data.generator import generate_synthetic_data
from backend.services.recon_service import ReconciliationService
from reconciliation import ReconciliationStatus

def test_full_dataset_reconciliation(tmp_path):
    # 1. Generate synthetic data in temp directory
    out_dir = str(tmp_path / "data")
    orders_p, payments_p, bank_p = generate_synthetic_data(output_dir=out_dir, num_records=120, seed=42)

    assert os.path.exists(orders_p)
    assert os.path.exists(payments_p)
    assert os.path.exists(bank_p)

    orders_df = pd.read_csv(orders_p)
    payments_df = pd.read_csv(payments_p)
    bank_df = pd.read_csv(bank_p)

    # 2. Instantiate service and run reconciliation
    service = ReconciliationService()
    service.results_csv_path = str(tmp_path / "reconciliation_results.csv")

    summary, results = service.run_reconciliation(orders_df, payments_df, bank_df)

    # 3. Assertions
    assert summary["total_records"] > 100
    assert summary["matched_records"] > 40
    assert summary["exception_records"] > 0
    assert summary["match_rate_pct"] > 0.0
    assert os.path.exists(service.results_csv_path)

    # Verify CSV file contents
    results_df = pd.read_csv(service.results_csv_path)
    assert "Order ID" in results_df.columns
    assert "Status" in results_df.columns
    assert "Confidence" in results_df.columns

    # Verify all expected status classifications exist in results
    statuses_in_results = set(results_df["Status"].tolist())
    assert ReconciliationStatus.MATCHED.value in statuses_in_results
    assert ReconciliationStatus.AMOUNT_MISMATCH.value in statuses_in_results
    assert ReconciliationStatus.MISSING_PAYMENT.value in statuses_in_results
    assert ReconciliationStatus.MISSING_BANK_TRANSACTION.value in statuses_in_results
    assert ReconciliationStatus.DUPLICATE_TRANSACTION.value in statuses_in_results
    assert ReconciliationStatus.DATE_MISMATCH.value in statuses_in_results
    assert ReconciliationStatus.REFERENCE_MISMATCH.value in statuses_in_results
    assert ReconciliationStatus.PARTIAL_PAYMENT.value in statuses_in_results

