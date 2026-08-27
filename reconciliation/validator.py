"""
Data Validation and Normalization Preprocessing Layer
Validates required fields, normalizes types, dates, amounts, and flags schema errors or duplicates.
Does NOT silently delete records.
"""

from datetime import datetime
import re
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
from .models import OrderRecord, PaymentRecord, BankRecord, ValidationError

class DataValidator:
    def __init__(self):
        self.validation_errors: List[ValidationError] = []

    def normalize_amount(self, val: Any, record_type: str, record_id: str, field_name: str) -> float:
        if pd.isna(val) or val is None or str(val).strip() == "":
            self.validation_errors.append(ValidationError(
                record_type=record_type, record_id=str(record_id), field_name=field_name, error_message="Missing amount"
            ))
            return 0.0
        try:
            # Clean dollar signs, commas, whitespace
            cleaned = re.sub(r"[^\d.-]", "", str(val))
            return round(float(cleaned), 2)
        except Exception as e:
            self.validation_errors.append(ValidationError(
                record_type=record_type, record_id=str(record_id), field_name=field_name, error_message=f"Invalid amount format '{val}': {str(e)}"
            ))
            return 0.0

    def parse_datetime(self, val: Any, record_type: str, record_id: str, field_name: str) -> Optional[datetime]:
        if pd.isna(val) or val is None or str(val).strip() == "":
            return None
        val_str = str(val).strip()
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y"
        ]
        for fmt in date_formats:
            try:
                return datetime.strptime(val_str, fmt)
            except ValueError:
                continue
        
        self.validation_errors.append(ValidationError(
            record_type=record_type, record_id=str(record_id), field_name=field_name, error_message=f"Could not parse date '{val_str}'"
        ))
        return None

    def validate_and_normalize_orders(self, orders_df: pd.DataFrame) -> Tuple[List[OrderRecord], List[ValidationError]]:
        orders: List[OrderRecord] = []
        required_fields = ["order_id", "expected_amount"]

        for idx, row in orders_df.iterrows():
            order_id = str(row.get("order_id", "")).strip().upper()
            if not order_id or pd.isna(row.get("order_id")):
                order_id = f"UNKNOWN_ORD_{idx}"
                self.validation_errors.append(ValidationError(
                    record_type="Order", record_id=order_id, field_name="order_id", error_message="Missing required order_id"
                ))

            customer_id = str(row.get("customer_id", "UNKNOWN")).strip().upper()
            currency = str(row.get("currency", "INR")).strip().upper()
            payment_status = str(row.get("payment_status", "UNKNOWN")).strip().upper()

            amount = self.normalize_amount(row.get("expected_amount"), "Order", order_id, "expected_amount")
            order_dt = self.parse_datetime(row.get("order_date"), "Order", order_id, "order_date")

            orders.append(OrderRecord(
                order_id=order_id,
                customer_id=customer_id,
                order_date=order_dt,
                expected_amount=amount,
                currency=currency,
                payment_status=payment_status,
                raw_data=row.to_dict()
            ))

        return orders, self.validation_errors

    def validate_and_normalize_payments(self, payments_df: pd.DataFrame) -> Tuple[List[PaymentRecord], List[ValidationError]]:
        payments: List[PaymentRecord] = []
        seen_txn_ids: Dict[str, int] = {}

        for idx, row in payments_df.iterrows():
            payment_id = str(row.get("payment_id", f"PAY_UNK_{idx}")).strip().upper()
            order_id = str(row.get("order_id", "")).strip().upper()
            txn_id = str(row.get("transaction_id", "")).strip().upper()

            if not txn_id or pd.isna(row.get("transaction_id")):
                txn_id = f"NO_TXN_{idx}"
                self.validation_errors.append(ValidationError(
                    record_type="Payment", record_id=payment_id, field_name="transaction_id", error_message="Missing transaction_id"
                ))

            # Duplicate transaction ID detection
            if txn_id in seen_txn_ids:
                seen_txn_ids[txn_id] += 1
                self.validation_errors.append(ValidationError(
                    record_type="Payment", record_id=payment_id, field_name="transaction_id", error_message=f"Duplicate transaction ID '{txn_id}' detected"
                ))
            else:
                seen_txn_ids[txn_id] = 1

            paid_amount = self.normalize_amount(row.get("paid_amount"), "Payment", payment_id, "paid_amount")
            payment_dt = self.parse_datetime(row.get("payment_date"), "Payment", payment_id, "payment_date")
            pay_status = str(row.get("payment_status", "UNKNOWN")).strip().upper()
            pay_method = str(row.get("payment_method", "UNKNOWN")).strip().upper()

            payments.append(PaymentRecord(
                payment_id=payment_id,
                order_id=order_id,
                transaction_id=txn_id,
                payment_date=payment_dt,
                paid_amount=paid_amount,
                payment_status=pay_status,
                payment_method=pay_method,
                raw_data=row.to_dict()
            ))

        return payments, self.validation_errors

    def validate_and_normalize_bank_txns(self, bank_df: pd.DataFrame) -> Tuple[List[BankRecord], List[ValidationError]]:
        bank_txns: List[BankRecord] = []
        seen_bank_ids: Dict[str, int] = {}

        for idx, row in bank_df.iterrows():
            bank_id = str(row.get("bank_transaction_id", f"BNK_UNK_{idx}")).strip().upper()
            txn_ref = str(row.get("transaction_reference", "")).strip().upper()

            if bank_id in seen_bank_ids:
                self.validation_errors.append(ValidationError(
                    record_type="BankTransaction", record_id=bank_id, field_name="bank_transaction_id", error_message=f"Duplicate bank_transaction_id '{bank_id}'"
                ))
            else:
                seen_bank_ids[bank_id] = 1

            rec_amount = self.normalize_amount(row.get("received_amount"), "BankTransaction", bank_id, "received_amount")
            bank_dt = self.parse_datetime(row.get("transaction_date"), "BankTransaction", bank_id, "transaction_date")
            bank_status = str(row.get("bank_status", "SETTLED")).strip().upper()

            bank_txns.append(BankRecord(
                bank_transaction_id=bank_id,
                transaction_reference=txn_ref,
                transaction_date=bank_dt,
                received_amount=rec_amount,
                bank_status=bank_status,
                raw_data=row.to_dict()
            ))

        return bank_txns, self.validation_errors

