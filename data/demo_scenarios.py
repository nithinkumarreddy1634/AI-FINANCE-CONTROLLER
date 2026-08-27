"""
Demo Scenarios Generator
Creates the 6 specific demo scenario dataset files for testing Phase 2 AI Controller logic.
"""

import os
import pandas as pd

def generate_demo_scenarios(output_dir: str = "data/demo"):
    os.makedirs(output_dir, exist_ok=True)

    orders = [
        # Scenario 1: Exact Match
        {"order_id": "SCENARIO_01_EXACT", "customer_id": "CUST_S1", "order_date": "2026-02-01 10:00:00", "expected_amount": 2500.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Scenario 2: Partial Payment
        {"order_id": "SCENARIO_02_PARTIAL", "customer_id": "CUST_S2", "order_date": "2026-02-01 11:00:00", "expected_amount": 5000.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Scenario 3: Reference Difference
        {"order_id": "ORD-1042", "customer_id": "CUST_S3", "order_date": "2026-02-01 12:00:00", "expected_amount": 1800.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Scenario 4: Missing Bank Transaction
        {"order_id": "SCENARIO_04_NOBANK", "customer_id": "CUST_S4", "order_date": "2026-02-01 13:00:00", "expected_amount": 3200.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Scenario 5: Duplicate
        {"order_id": "SCENARIO_05_DUP", "customer_id": "CUST_S5", "order_date": "2026-02-01 14:00:00", "expected_amount": 4000.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Scenario 6: Insufficient Evidence
        {"order_id": "SCENARIO_06_MISSING", "customer_id": "CUST_S6", "order_date": "2026-02-01 15:00:00", "expected_amount": 1500.0, "currency": "INR", "payment_status": "PENDING"}
    ]

    payments = [
        # Scenario 1
        {"payment_id": "PAY_S1", "order_id": "SCENARIO_01_EXACT", "transaction_id": "TXN_S1", "payment_date": "2026-02-01 10:05:00", "paid_amount": 2500.0, "payment_status": "SUCCESS", "payment_method": "UPI"},
        # Scenario 2
        {"payment_id": "PAY_S2", "order_id": "SCENARIO_02_PARTIAL", "transaction_id": "TXN_S2", "payment_date": "2026-02-01 11:05:00", "paid_amount": 5000.0, "payment_status": "SUCCESS", "payment_method": "CREDIT_CARD"},
        # Scenario 3
        {"payment_id": "PAY_S3", "order_id": "ORD-1042", "transaction_id": "1042", "payment_date": "2026-02-01 12:05:00", "paid_amount": 1800.0, "payment_status": "SUCCESS", "payment_method": "UPI"},
        # Scenario 4
        {"payment_id": "PAY_S4", "order_id": "SCENARIO_04_NOBANK", "transaction_id": "TXN_S4", "payment_date": "2026-02-01 13:05:00", "paid_amount": 3200.0, "payment_status": "SUCCESS", "payment_method": "NET_BANKING"},
        # Scenario 5
        {"payment_id": "PAY_S5_1", "order_id": "SCENARIO_05_DUP", "transaction_id": "TXN_S5", "payment_date": "2026-02-01 14:05:00", "paid_amount": 4000.0, "payment_status": "SUCCESS", "payment_method": "UPI"},
        {"payment_id": "PAY_S5_2", "order_id": "SCENARIO_05_DUP", "transaction_id": "TXN_S5", "payment_date": "2026-02-01 14:10:00", "paid_amount": 4000.0, "payment_status": "SUCCESS", "payment_method": "UPI"}
        # Scenario 6: No payment logged
    ]

    bank_txns = [
        # Scenario 1
        {"bank_transaction_id": "BNK_S1", "transaction_reference": "REF-TXN_S1", "transaction_date": "2026-02-02 09:00:00", "received_amount": 2500.0, "bank_status": "SETTLED"},
        # Scenario 2
        {"bank_transaction_id": "BNK_S2", "transaction_reference": "REF-TXN_S2", "transaction_date": "2026-02-02 09:00:00", "received_amount": 4500.0, "bank_status": "SETTLED"},
        # Scenario 3 (Reference difference: PAY-1042 vs ORD-1042 / TXN_1042)
        {"bank_transaction_id": "BNK_S3", "transaction_reference": "PAY-1042", "transaction_date": "2026-02-02 09:00:00", "received_amount": 1800.0, "bank_status": "SETTLED"},
        # Scenario 4: No bank transaction
        # Scenario 5
        {"bank_transaction_id": "BNK_S5", "transaction_reference": "REF-TXN_S5", "transaction_date": "2026-02-02 09:00:00", "received_amount": 4000.0, "bank_status": "SETTLED"}
        # Scenario 6: No bank transaction
    ]

    pd.DataFrame(orders).to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    pd.DataFrame(payments).to_csv(os.path.join(output_dir, "payments.csv"), index=False)
    pd.DataFrame(bank_txns).to_csv(os.path.join(output_dir, "bank_transactions.csv"), index=False)

    print(f"Demo scenarios dataset created in '{output_dir}'!")

if __name__ == "__main__":
    generate_demo_scenarios()
