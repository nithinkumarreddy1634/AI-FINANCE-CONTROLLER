"""
Data models for payment reconciliation engine.
Defines structures for Orders, Payments, Bank Transactions, and Reconciliation Results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    MISSING_PAYMENT = "MISSING_PAYMENT"
    MISSING_BANK_TRANSACTION = "MISSING_BANK_TRANSACTION"
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    DATE_MISMATCH = "DATE_MISMATCH"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    UNRESOLVED = "UNRESOLVED"

@dataclass
class OrderRecord:
    order_id: str
    customer_id: str
    order_date: Optional[datetime]
    expected_amount: float
    currency: str
    payment_status: str
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PaymentRecord:
    payment_id: str
    order_id: str
    transaction_id: str
    payment_date: Optional[datetime]
    paid_amount: float
    payment_status: str
    payment_method: str
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BankRecord:
    bank_transaction_id: str
    transaction_reference: str
    transaction_date: Optional[datetime]
    received_amount: float
    bank_status: str
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationError:
    record_type: str
    record_id: str
    field_name: str
    error_message: str

@dataclass
class ReconciliationResultRecord:
    order_id: str
    customer_id: str
    expected_amount: float
    paid_amount: Optional[float]
    bank_received_amount: Optional[float]
    transaction_id: Optional[str]
    payment_id: Optional[str]
    bank_transaction_id: Optional[str]
    status: ReconciliationStatus
    confidence_score: float
    discrepancy_amount: float
    explanation: str
    reasons: List[str] = field(default_factory=list)
    order_date: Optional[str] = None
    payment_date: Optional[str] = None
    bank_date: Optional[str] = None

