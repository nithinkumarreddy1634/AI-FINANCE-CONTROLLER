"""
Ground-Truth Evaluation Dataset Generator (500 Records)
Generates 500 ground-truth labeled synthetic financial cases using fixed random seed 2026.
Creates evaluation datasets: orders_eval.csv, payments_eval.csv, bank_transactions_eval.csv, and ground_truth.csv.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_evaluation_dataset(output_dir: str = "evaluation", seed: int = 2026, total_count: int = 500):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(seed)

    orders = []
    payments = []
    bank_txns = []
    ground_truth = []

    start_date = datetime(2026, 1, 1, 10, 0, 0)

    # Categories breakdown totaling 500
    counts = {
        "EXACT_MATCH": 200,
        "PARTIAL_PAYMENT": 50,
        "AMOUNT_MISMATCH": 50,
        "MISSING_PAYMENT": 40,
        "MISSING_BANK_TXN": 40,
        "DUPLICATE": 30,
        "DATE_MISMATCH": 30,
        "REFERENCE_MISMATCH": 30,
        "MULTIPLE_CANDIDATES": 30
    }

    curr_id = 1

    for category, num_cases in counts.items():
        for i in range(num_cases):
            order_id = f"EVAL_{curr_id:04d}"
            customer_id = f"CUST_EVAL_{random.randint(100, 999)}"
            order_date = start_date + timedelta(hours=curr_id * 2, minutes=random.randint(0, 50))
            expected_amount = round(random.uniform(500.0, 15000.0), 2)
            txn_id = f"TXN_EVAL_{curr_id:04d}"
            pay_id = f"PAY_EVAL_{curr_id:04d}"
            bank_id = f"BNK_EVAL_{curr_id:04d}"

            if category == "EXACT_MATCH":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": expected_amount, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "EXACT_MATCH",
                    "expected_decision": "LIKELY_MATCH",
                    "expected_action": "AUTO_RECONCILE",
                    "expected_match": True,
                    "ground_truth_note": "Exact match across order, payment, and bank settlement."
                })

            elif category == "PARTIAL_PAYMENT":
                paid_amt = round(expected_amount * 0.90, 2)
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": paid_amt, "payment_status": "SUCCESS", "payment_method": "CREDIT_CARD"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": paid_amt, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "PARTIAL_PAYMENT",
                    "expected_decision": "PARTIAL_MATCH",
                    "expected_action": "MARK_FOR_REVIEW",
                    "expected_match": False,
                    "ground_truth_note": f"Partial payment received: ₹{paid_amt} vs expected ₹{expected_amount}."
                })

            elif category == "AMOUNT_MISMATCH":
                received_amt = round(expected_amount - random.uniform(50.0, 300.0), 2)
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": received_amt, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "AMOUNT_MISMATCH",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "MARK_FOR_REVIEW",
                    "expected_match": False,
                    "ground_truth_note": f"Amount mismatch: Bank received ₹{received_amt} vs expected ₹{expected_amount}."
                })

            elif category == "MISSING_PAYMENT":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "PENDING"})
                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": None,
                    "exception_type": "MISSING_PAYMENT",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "ESCALATE",
                    "expected_match": False,
                    "ground_truth_note": "No gateway payment record exists."
                })

            elif category == "MISSING_BANK_TXN":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "NET_BANKING"})
                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "MISSING_BANK_TRANSACTION",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "ESCALATE",
                    "expected_match": False,
                    "ground_truth_note": "No bank settlement transaction credit exists."
                })

            elif category == "DUPLICATE":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": expected_amount, "bank_status": "SETTLED"})
                # Duplicate bank record
                bank_txns.append({"bank_transaction_id": f"{bank_id}_DUP", "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1, hours=2)), "received_amount": expected_amount, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "DUPLICATE_TRANSACTION",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "MARK_FOR_REVIEW",
                    "expected_match": False,
                    "ground_truth_note": "Duplicate bank settlement credit detected."
                })

            elif category == "DATE_MISMATCH":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=2)), "received_amount": expected_amount, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "DATE_MISMATCH",
                    "expected_decision": "LIKELY_MATCH",
                    "expected_action": "MARK_FOR_REVIEW",
                    "expected_match": True,
                    "ground_truth_note": "Settlement date lag within acceptable 3-day policy window."
                })

            elif category == "REFERENCE_MISMATCH":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": bank_id, "transaction_reference": f"REF-{txn_id}_TYPO", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": expected_amount, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "REFERENCE_MISMATCH",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "MARK_FOR_REVIEW",
                    "expected_match": False,
                    "ground_truth_note": "Reference string typo in bank transaction."
                })

            elif category == "MULTIPLE_CANDIDATES":
                orders.append({"order_id": order_id, "customer_id": customer_id, "order_date": str(order_date), "expected_amount": expected_amount, "currency": "INR", "payment_status": "COMPLETED"})
                payments.append({"payment_id": pay_id, "order_id": order_id, "transaction_id": txn_id, "payment_date": str(order_date + timedelta(minutes=5)), "paid_amount": expected_amount, "payment_status": "SUCCESS", "payment_method": "UPI"})
                bank_txns.append({"bank_transaction_id": f"{bank_id}_A", "transaction_reference": f"REF-{txn_id}", "transaction_date": str(order_date + timedelta(days=1)), "received_amount": expected_amount, "bank_status": "SETTLED"})
                bank_txns.append({"bank_transaction_id": f"{bank_id}_B", "transaction_reference": f"REF-{txn_id}_ALT", "transaction_date": str(order_date + timedelta(days=5)), "received_amount": expected_amount - 100.0, "bank_status": "SETTLED"})

                ground_truth.append({
                    "order_id": order_id,
                    "transaction_id": txn_id,
                    "exception_type": "MULTIPLE_CANDIDATES",
                    "expected_decision": "UNRESOLVED",
                    "expected_action": "ESCALATE",
                    "expected_match": False,
                    "ground_truth_note": "Multiple ambiguous candidate bank settlements exist."
                })

            curr_id += 1

    pd.DataFrame(orders).to_csv(os.path.join(output_dir, "orders_eval.csv"), index=False)
    pd.DataFrame(payments).to_csv(os.path.join(output_dir, "payments_eval.csv"), index=False)
    pd.DataFrame(bank_txns).to_csv(os.path.join(output_dir, "bank_transactions_eval.csv"), index=False)
    pd.DataFrame(ground_truth).to_csv(os.path.join(output_dir, "ground_truth.csv"), index=False)

    print(f"Evaluation ground-truth dataset generated successfully in '{output_dir}' ({total_count} records).")

if __name__ == "__main__":
    generate_evaluation_dataset()
