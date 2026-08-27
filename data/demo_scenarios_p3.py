"""
Phase 3 Demo Scenarios Dataset Generator
Generates datasets for the 5 specific Phase 3 demo cases:
1. Settlement Date Difference (within 2-day policy window)
2. Partial Payment Shortfall
3. Multiple Candidate Bank Settlements
4. Missing Essential Evidence
5. AI Hallucination Protection
"""

import os
import pandas as pd

def generate_phase3_demo_scenarios(output_dir: str = "data/demo_p3"):
    os.makedirs(output_dir, exist_ok=True)

    orders = [
        # Demo 1: Settlement Date Difference
        {"order_id": "P3_DEMO_01_DATE", "customer_id": "CUST_P3_1", "order_date": "2026-02-10 10:00:00", "expected_amount": 2000.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Demo 2: Partial Payment Shortfall
        {"order_id": "P3_DEMO_02_PARTIAL", "customer_id": "CUST_P3_2", "order_date": "2026-02-10 11:00:00", "expected_amount": 5000.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Demo 3: Duplicate Candidates
        {"order_id": "P3_DEMO_03_CANDIDATES", "customer_id": "CUST_P3_3", "order_date": "2026-02-10 12:00:00", "expected_amount": 3500.0, "currency": "INR", "payment_status": "COMPLETED"},
        # Demo 4: Missing Evidence
        {"order_id": "P3_DEMO_04_NOEVIDENCE", "customer_id": "CUST_P3_4", "order_date": "2026-02-10 13:00:00", "expected_amount": 1200.0, "currency": "INR", "payment_status": "PENDING"},
        # Demo 5: AI Hallucination Protection
        {"order_id": "P3_DEMO_05_HALLUCINATION", "customer_id": "CUST_P3_5", "order_date": "2026-02-10 14:00:00", "expected_amount": 4200.0, "currency": "INR", "payment_status": "COMPLETED"}
    ]

    payments = [
        # Demo 1
        {"payment_id": "PAY_P3_1", "order_id": "P3_DEMO_01_DATE", "transaction_id": "TXN_P3_1", "payment_date": "2026-02-10 10:05:00", "paid_amount": 2000.0, "payment_status": "SUCCESS", "payment_method": "UPI"},
        # Demo 2
        {"payment_id": "PAY_P3_2", "order_id": "P3_DEMO_02_PARTIAL", "transaction_id": "TXN_P3_2", "payment_date": "2026-02-10 11:05:00", "paid_amount": 5000.0, "payment_status": "SUCCESS", "payment_method": "CREDIT_CARD"},
        # Demo 3
        {"payment_id": "PAY_P3_3", "order_id": "P3_DEMO_03_CANDIDATES", "transaction_id": "TXN_P3_3", "payment_date": "2026-02-10 12:05:00", "paid_amount": 3500.0, "payment_status": "SUCCESS", "payment_method": "UPI"},
        # Demo 4: No payment
        # Demo 5
        {"payment_id": "PAY_P3_5", "order_id": "P3_DEMO_05_HALLUCINATION", "transaction_id": "TXN_P3_5", "payment_date": "2026-02-10 14:05:00", "paid_amount": 4200.0, "payment_status": "SUCCESS", "payment_method": "UPI"}
    ]

    bank_txns = [
        # Demo 1: Settlement date 2 days later (within 3-day window)
        {"bank_transaction_id": "BNK_P3_1", "transaction_reference": "REF-TXN_P3_1", "transaction_date": "2026-02-12 09:00:00", "received_amount": 2000.0, "bank_status": "SETTLED"},
        # Demo 2: Partial payment received 4500 instead of 5000
        {"bank_transaction_id": "BNK_P3_2", "transaction_reference": "REF-TXN_P3_2", "transaction_date": "2026-02-11 09:00:00", "received_amount": 4500.0, "bank_status": "SETTLED"},
        # Demo 3: Candidate A (Stronger match: exact amount, close date) vs Candidate B (Weaker match: different date/amount)
        {"bank_transaction_id": "BNK_P3_3A", "transaction_reference": "REF-TXN_P3_3", "transaction_date": "2026-02-11 09:00:00", "received_amount": 3500.0, "bank_status": "SETTLED"},
        {"bank_transaction_id": "BNK_P3_3B", "transaction_reference": "REF-TXN_P3_3_ALT", "transaction_date": "2026-02-18 09:00:00", "received_amount": 3000.0, "bank_status": "SETTLED"},
        # Demo 4: No bank transaction
        # Demo 5: Received amount 3800 vs expected 4200 (triggers Post-LLM rule rejection if AI claimed exact match)
        {"bank_transaction_id": "BNK_P3_5", "transaction_reference": "REF-TXN_P3_5", "transaction_date": "2026-02-11 09:00:00", "received_amount": 3800.0, "bank_status": "SETTLED"}
    ]

    pd.DataFrame(orders).to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    pd.DataFrame(payments).to_csv(os.path.join(output_dir, "payments.csv"), index=False)
    pd.DataFrame(bank_txns).to_csv(os.path.join(output_dir, "bank_transactions.csv"), index=False)

    print(f"Phase 3 Demo scenarios created in '{output_dir}'.")

if __name__ == "__main__":
    generate_phase3_demo_scenarios()

