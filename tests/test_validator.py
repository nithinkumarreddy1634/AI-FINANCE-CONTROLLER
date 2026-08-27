"""
Unit tests for DataValidator preprocessing and normalization.
"""

from datetime import datetime
import pandas as pd
from reconciliation import DataValidator

def test_amount_normalization():
    validator = DataValidator()
    assert validator.normalize_amount("2500.00", "Order", "ORD1", "amount") == 2500.00
    assert validator.normalize_amount("$1,499.50", "Order", "ORD2", "amount") == 1499.50
    assert validator.normalize_amount(None, "Order", "ORD3", "amount") == 0.0
    assert len(validator.validation_errors) == 1

def test_date_parsing():
    validator = DataValidator()
    dt = validator.parse_datetime("2026-01-15 10:30:00", "Order", "ORD1", "date")
    assert isinstance(dt, datetime)
    assert dt.year == 2026 and dt.month == 1 and dt.day == 15

    dt2 = validator.parse_datetime("15/01/2026", "Order", "ORD2", "date")
    assert isinstance(dt2, datetime)

def test_duplicate_transaction_detection():
    validator = DataValidator()
    df_payments = pd.DataFrame([
        {"payment_id": "PAY1", "order_id": "ORD1", "transaction_id": "TXN100", "paid_amount": 500},
        {"payment_id": "PAY2", "order_id": "ORD2", "transaction_id": "TXN100", "paid_amount": 500}
    ])
    payments, errors = validator.validate_and_normalize_payments(df_payments)
    assert len(payments) == 2
    assert any("Duplicate transaction ID" in err.error_message for err in errors)

