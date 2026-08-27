"""
Unit tests for DeterministicMatcher reconciliation rules.
Coverage for exact match, amount mismatch, missing payment, missing bank txn,
duplicate transaction, partial payment, date mismatch, reference mismatch.
"""

from datetime import datetime, timedelta
from reconciliation import (
    OrderRecord, PaymentRecord, BankRecord,
    DeterministicMatcher, ReconciliationStatus
)

def create_datetime(days_offset=0):
    return datetime(2026, 1, 10, 12, 0, 0) + timedelta(days=days_offset)

def test_exact_match():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD001", "CUST1", dt, 2500.0, "INR", "COMPLETED")]
    payments = [PaymentRecord("PAY001", "ORD001", "TXN001", dt, 2500.0, "SUCCESS", "UPI")]
    bank_txns = [BankRecord("BNK001", "REF-TXN001", dt + timedelta(days=1), 2500.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.MATCHED
    assert results[0].confidence_score == 100.0
    assert results[0].discrepancy_amount == 0.0

def test_amount_mismatch():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD002", "CUST2", dt, 3000.0, "INR", "COMPLETED")]
    payments = [PaymentRecord("PAY002", "ORD002", "TXN002", dt, 3000.0, "SUCCESS", "CREDIT_CARD")]
    bank_txns = [BankRecord("BNK002", "REF-TXN002", dt + timedelta(days=1), 2850.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.AMOUNT_MISMATCH
    assert results[0].discrepancy_amount == 150.0
    assert results[0].confidence_score < 100.0

def test_missing_payment():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD003", "CUST3", dt, 1500.0, "INR", "PENDING")]
    payments = []
    bank_txns = []

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.MISSING_PAYMENT
    assert results[0].discrepancy_amount == 1500.0

def test_missing_bank_transaction():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD004", "CUST4", dt, 2000.0, "INR", "COMPLETED")]
    payments = [PaymentRecord("PAY004", "ORD004", "TXN004", dt, 2000.0, "SUCCESS", "UPI")]
    bank_txns = []

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.MISSING_BANK_TRANSACTION
    assert results[0].discrepancy_amount == 2000.0

def test_duplicate_transaction():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD005", "CUST5", dt, 1000.0, "INR", "COMPLETED")]
    payments = [
        PaymentRecord("PAY005_1", "ORD005", "TXN005", dt, 1000.0, "SUCCESS", "UPI"),
        PaymentRecord("PAY005_2", "ORD005", "TXN005", dt + timedelta(minutes=5), 1000.0, "SUCCESS", "UPI")
    ]
    bank_txns = [BankRecord("BNK005", "REF-TXN005", dt + timedelta(days=1), 1000.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.DUPLICATE_TRANSACTION

def test_partial_payment():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD006", "CUST6", dt, 5000.0, "INR", "PARTIAL")]
    payments = [PaymentRecord("PAY006", "ORD006", "TXN006", dt, 2500.0, "PARTIAL_SUCCESS", "UPI")]
    bank_txns = [BankRecord("BNK006", "REF-TXN006", dt + timedelta(days=1), 2500.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.PARTIAL_PAYMENT
    assert results[0].discrepancy_amount == 2500.0

def test_date_mismatch():
    dt = create_datetime(0)
    late_dt = dt + timedelta(days=10)
    orders = [OrderRecord("ORD007", "CUST7", dt, 1200.0, "INR", "COMPLETED")]
    payments = [PaymentRecord("PAY007", "ORD007", "TXN007", dt, 1200.0, "SUCCESS", "UPI")]
    bank_txns = [BankRecord("BNK007", "REF-TXN007", late_dt, 1200.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.DATE_MISMATCH

def test_reference_mismatch():
    dt = create_datetime(0)
    orders = [OrderRecord("ORD008", "CUST8", dt, 800.0, "INR", "COMPLETED")]
    payments = [PaymentRecord("PAY008", "ORD008", "TXN008", dt, 800.0, "SUCCESS", "UPI")]
    bank_txns = [BankRecord("BNK008", "ERR-REF-TXN008-WRONG", dt + timedelta(days=1), 800.0, "SETTLED")]

    matcher = DeterministicMatcher()
    results = matcher.reconcile(orders, payments, bank_txns)

    assert len(results) == 1
    assert results[0].status == ReconciliationStatus.REFERENCE_MISMATCH

