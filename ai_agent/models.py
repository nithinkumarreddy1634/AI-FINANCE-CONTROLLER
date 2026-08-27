"""
AI Agent Data Models & Enums
Defines structures for Evidence Packages, Structured AI Decision Outputs,
Human Review Inputs, and Audit Trail Records.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

class AIDecisionEnum(str, Enum):
    LIKELY_MATCH = "LIKELY_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    DATE_MISMATCH = "DATE_MISMATCH"
    DUPLICATE = "DUPLICATE"
    MISSING_PAYMENT = "MISSING_PAYMENT"
    MISSING_BANK_TRANSACTION = "MISSING_BANK_TRANSACTION"
    UNRESOLVED = "UNRESOLVED"

class AIActionEnum(str, Enum):
    AUTO_RECONCILE = "AUTO_RECONCILE"
    MARK_FOR_REVIEW = "MARK_FOR_REVIEW"
    ESCALATE = "ESCALATE"
    NO_ACTION = "NO_ACTION"

class HumanDecisionEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"

@dataclass
class EvidencePackage:
    order_id: str
    customer_id: Optional[str] = None
    order_date: Optional[str] = None
    expected_amount: Optional[float] = None
    currency: Optional[str] = "INR"
    order_payment_status: Optional[str] = None

    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[str] = None
    paid_amount: Optional[float] = None
    gateway_payment_status: Optional[str] = None
    payment_method: Optional[str] = None

    bank_transaction_id: Optional[str] = None
    transaction_reference: Optional[str] = None
    transaction_date: Optional[str] = None
    received_amount: Optional[float] = None
    bank_status: Optional[str] = None

    phase1_status: Optional[str] = None
    phase1_confidence: Optional[float] = None
    phase1_explanation: Optional[str] = None
    detected_discrepancies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": {
                "order_id": self.order_id,
                "customer_id": self.customer_id,
                "order_date": self.order_date,
                "expected_amount": self.expected_amount,
                "currency": self.currency,
                "payment_status": self.order_payment_status
            },
            "payment": {
                "payment_id": self.payment_id,
                "transaction_id": self.transaction_id,
                "payment_date": self.payment_date,
                "paid_amount": self.paid_amount,
                "payment_status": self.gateway_payment_status,
                "payment_method": self.payment_method
            },
            "bank": {
                "bank_transaction_id": self.bank_transaction_id,
                "transaction_reference": self.transaction_reference,
                "transaction_date": self.transaction_date,
                "received_amount": self.received_amount,
                "bank_status": self.bank_status
            },
            "phase1_analysis": {
                "reconciliation_status": self.phase1_status,
                "rule_based_confidence": self.phase1_confidence,
                "explanation": self.phase1_explanation,
                "detected_discrepancies": self.detected_discrepancies
            }
        }

@dataclass
class AIDecisionOutput:
    order_id: str
    decision: AIDecisionEnum
    confidence: float
    reason: str
    evidence: List[str]
    discrepancies: List[str]
    recommended_action: AIActionEnum
    requires_human_review: bool
    investigation_id: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "decision": self.decision.value if isinstance(self.decision, Enum) else self.decision,
            "confidence": self.confidence,
            "reason": self.reason,
            "evidence": self.evidence,
            "discrepancies": self.discrepancies,
            "recommended_action": self.recommended_action.value if isinstance(self.recommended_action, Enum) else self.recommended_action,
            "requires_human_review": self.requires_human_review,
            "investigation_id": self.investigation_id,
            "timestamp": self.timestamp
        }

@dataclass
class HumanReviewInput:
    reviewer_name: str
    decision: HumanDecisionEnum
    reviewer_note: str
    modified_status: Optional[str] = None

@dataclass
class AuditRecord:
    investigation_id: str
    transaction_id: str
    order_id: str
    timestamp: str
    rule_decision: str
    rule_confidence: float
    ai_decision: str
    ai_confidence: float
    recommended_action: str
    requires_human_review: bool
    human_decision: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_note: Optional[str] = None
    review_timestamp: Optional[str] = None
    evidence_summary: List[str] = field(default_factory=list)
    ai_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "investigation_id": self.investigation_id,
            "transaction_id": self.transaction_id,
            "order_id": self.order_id,
            "timestamp": self.timestamp,
            "rule_decision": self.rule_decision,
            "rule_confidence": self.rule_confidence,
            "ai_decision": self.ai_decision,
            "ai_confidence": self.ai_confidence,
            "recommended_action": self.recommended_action,
            "requires_human_review": self.requires_human_review,
            "human_decision": self.human_decision,
            "reviewer_name": self.reviewer_name,
            "reviewer_note": self.reviewer_note,
            "review_timestamp": self.review_timestamp,
            "evidence_summary": self.evidence_summary,
            "ai_reason": self.ai_reason
        }

