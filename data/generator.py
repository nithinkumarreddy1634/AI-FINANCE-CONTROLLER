"""
Synthetic Financial Dataset Generator
Generates reproducible synthetic financial datasets for testing payment reconciliation.
Creates: orders.csv, payments.csv, bank_transactions.csv (100+ records)
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_synthetic_data(output_dir: str = "data", num_records: int = 120, seed: int = 42):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    currencies = ["INR"]
    payment_methods = ["UPI", "CREDIT_CARD", "NET_BANKING", "DEBIT_CARD", "WALLET"]
    
    start_date = datetime(2026, 1, 1)

    orders = []
    payments = []
    bank_txns = []

    # Distribution of cases:
    # 0-55: Exact Match
    # 56-65: Amount Mismatch (fee deduction / variance)
    # 66-75: Missing Bank Transaction (pending settlement)
    # 76-85: Missing Payment Record (unpaid order)
    # 86-92: Duplicate Payment Transaction
    # 93-98: Date Mismatch (>3 days settlement lag)
    # 99-105: Reference Mismatch (typo in bank reference)
    # 106-112: Partial Payment
    # 113-120: Unexpected Extra Bank Transaction (no order)

    bank_txn_counter = 1000

    for i in range(1, num_records + 1):
        order_id = f"ORD{i:04d}"
        cust_id = f"CUST{(i % 30) + 1:03d}"
        days_offset = (i // 3) % 40
        order_dt = start_date + timedelta(days=days_offset, hours=random.randint(8, 20), minutes=random.randint(0, 59))
        expected_amt = round(random.choice([499.0, 999.0, 1499.0, 2500.0, 3000.0, 4999.0, 12000.0, 1500.0]), 2)
        currency = "INR"

        txn_id = f"TXN{i:04d}"
        payment_id = f"PAY{i:04d}"
        payment_dt = order_dt + timedelta(minutes=random.randint(1, 45))
        pay_method = random.choice(payment_methods)

        bank_txn_counter += 1
        bank_txn_id = f"BNK{bank_txn_counter:04d}"
        txn_ref = f"REF-{txn_id}"
        bank_dt = payment_dt + timedelta(days=random.randint(1, 2))

        if i <= 55:
            # CASE 1: Exact Match
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": txn_ref,
                "transaction_date": bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": expected_amt,
                "bank_status": "SETTLED"
            })

        elif 56 <= i <= 65:
            # CASE 2: Amount Mismatch (e.g., fee deduction or mismatch)
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            # Bank receives slightly less due to gateway charges or discrepancy
            mismatched_amt = round(expected_amt * random.choice([0.95, 0.98, 0.90]), 2)
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": txn_ref,
                "transaction_date": bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": mismatched_amt,
                "bank_status": "SETTLED"
            })

        elif 66 <= i <= 75:
            # CASE 3: Missing Bank Transaction (pending settlement)
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            # No bank record generated

        elif 76 <= i <= 85:
            # CASE 4: Missing Payment Record (unpaid order)
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "PENDING"
            })
            # No payment record and no bank transaction generated

        elif 86 <= i <= 92:
            # CASE 5: Duplicate Payment Transaction
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            # Original payment
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            # Duplicate payment record with same transaction_id
            payments.append({
                "payment_id": f"PAY{i:04d}_DUP",
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": (payment_dt + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": txn_ref,
                "transaction_date": bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": expected_amt,
                "bank_status": "SETTLED"
            })

        elif 93 <= i <= 98:
            # CASE 6: Date Mismatch (>5 days lag)
            late_bank_dt = payment_dt + timedelta(days=random.randint(8, 14))
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": txn_ref,
                "transaction_date": late_bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": expected_amt,
                "bank_status": "SETTLED"
            })

        elif 99 <= i <= 105:
            # CASE 7: Reference Mismatch
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "COMPLETED"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": expected_amt,
                "payment_status": "SUCCESS",
                "payment_method": pay_method
            })
            # Malformed transaction reference in bank statement
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": f"ERR-REF-{txn_id}-WRONG",
                "transaction_date": bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": expected_amt,
                "bank_status": "SETTLED"
            })

        elif 106 <= i <= 112:
            # CASE 8: Partial Payment
            partial_amt = round(expected_amt * 0.5, 2)
            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expected_amount": expected_amt,
                "currency": currency,
                "payment_status": "PARTIAL"
            })
            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "transaction_id": txn_id,
                "payment_date": payment_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "paid_amount": partial_amt,
                "payment_status": "PARTIAL_SUCCESS",
                "payment_method": pay_method
            })
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": txn_ref,
                "transaction_date": bank_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": partial_amt,
                "bank_status": "SETTLED"
            })

        else:
            # CASE 9: Unexpected Extra Bank Transaction (no order)
            extra_dt = start_date + timedelta(days=random.randint(5, 25))
            bank_txns.append({
                "bank_transaction_id": bank_txn_id,
                "transaction_reference": f"UNEXPECTED-REF-{i}",
                "transaction_date": extra_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "received_amount": round(random.uniform(500, 5000), 2),
                "bank_status": "SETTLED"
            })

    orders_df = pd.DataFrame(orders)
    payments_df = pd.DataFrame(payments)
    bank_df = pd.DataFrame(bank_txns)

    orders_path = os.path.join(output_dir, "orders.csv")
    payments_path = os.path.join(output_dir, "payments.csv")
    bank_path = os.path.join(output_dir, "bank_transactions.csv")

    orders_df.to_csv(orders_path, index=False)
    payments_df.to_csv(payments_path, index=False)
    bank_df.to_csv(bank_path, index=False)

    print(f"Dataset generated successfully in '{output_dir}':")
    print(f" - Orders: {len(orders_df)} records")
    print(f" - Payments: {len(payments_df)} records")
    print(f" - Bank Transactions: {len(bank_df)} records")

    return orders_path, payments_path, bank_path

if __name__ == "__main__":
    generate_synthetic_data()

