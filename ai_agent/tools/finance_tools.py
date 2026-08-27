"""
Controlled Finance Agent Tools
Provides strictly controlled, auditable tool implementations for AI Agent execution.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
from backend.services.recon_service import ReconciliationService
from knowledge.retriever import PolicyRetriever

recon_service = ReconciliationService()
policy_retriever = PolicyRetriever()

def get_order(order_id: str) -> Dict[str, Any]:
    txns = recon_service.get_transactions(search=order_id)
    if txns:
        t = txns[0]
        return {
            "order_id": t["order_id"],
            "customer_id": t["customer_id"],
            "expected_amount": t["expected_amount"],
            "order_date": t.get("order_date")
        }
    return {"error": f"Order ID '{order_id}' not found."}

def get_payment(payment_id: str) -> Dict[str, Any]:
    txns = recon_service.get_transactions(search=payment_id)
    if txns:
        t = txns[0]
        return {
            "payment_id": t.get("payment_id"),
            "transaction_id": t.get("transaction_id"),
            "paid_amount": t.get("paid_amount"),
            "payment_date": t.get("payment_date")
        }
    return {"error": f"Payment ID '{payment_id}' not found."}

def get_bank_transaction(bank_transaction_id: str) -> Dict[str, Any]:
    txns = recon_service.get_transactions(search=bank_transaction_id)
    if txns:
        t = txns[0]
        return {
            "bank_transaction_id": t.get("bank_transaction_id"),
            "transaction_reference": f"REF-{t.get('transaction_id')}" if t.get('transaction_id') else None,
            "bank_received_amount": t.get("bank_received_amount"),
            "bank_date": t.get("bank_date")
        }
    return {"error": f"Bank Transaction ID '{bank_transaction_id}' not found."}

def search_transactions(query: str) -> List[Dict[str, Any]]:
    return recon_service.get_transactions(search=query)

def compare_transactions(id1: str, id2: str) -> Dict[str, Any]:
    res1 = recon_service.get_transactions(search=id1)
    res2 = recon_service.get_transactions(search=id2)
    t1 = res1[0] if res1 else {}
    t2 = res2[0] if res2 else {}

    amount_diff = abs((t1.get("expected_amount") or 0.0) - (t2.get("expected_amount") or 0.0))
    return {
        "record_1": {"id": id1, "amount": t1.get("expected_amount"), "status": t1.get("status")},
        "record_2": {"id": id2, "amount": t2.get("expected_amount"), "status": t2.get("status")},
        "amount_difference": round(amount_diff, 2)
    }

def calculate_amount_difference(expected: float, actual: float) -> Dict[str, Any]:
    diff = round(abs(expected - actual), 2)
    pct = round((diff / max(expected, 1.0)) * 100, 2)
    return {
        "expected": expected,
        "actual": actual,
        "difference": diff,
        "variance_pct": pct
    }

def calculate_date_difference(date1_str: str, date2_str: str) -> Dict[str, Any]:
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            d1 = datetime.strptime(date1_str.split(".")[0], fmt)
            d2 = datetime.strptime(date2_str.split(".")[0], fmt)
            days = abs((d2 - d1).days)
            return {"date1": date1_str, "date2": date2_str, "days_difference": days}
        except ValueError:
            continue
    return {"error": f"Could not parse dates '{date1_str}' and '{date2_str}'."}

def search_finance_policy(query: str) -> List[Dict[str, Any]]:
    citations = policy_retriever.retrieve_policy(query, top_k=2)
    return [c.to_dict() for c in citations]

def get_reconciliation_result(transaction_id: str) -> Dict[str, Any]:
    txns = recon_service.get_transactions(search=transaction_id)
    if txns:
        return txns[0]
    return {"error": f"Reconciliation result for '{transaction_id}' not found."}

