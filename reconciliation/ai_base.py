"""
Phase 2 Preparation: AI Finance Controller Agent Interface
Defines abstract contracts and schemas for Phase 2 LLM/Agentic exception handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .models import ReconciliationResultRecord, ReconciliationStatus

@dataclass
class AIAgentRecommendation:
    order_id: str
    recommended_status: ReconciliationStatus
    ai_confidence_score: float
    reasoning_summary: str
    evidence_compared: List[str]
    suggested_action: str  # e.g., "AUTO_RESOLVE", "MANUAL_AUDIT", "REFUND_CUSTOMER", "CONTACT_BANK"
    requires_human_escalation: bool

class AIFinanceAgentInterface(ABC):
    """
    Abstract interface for Phase 2 AI Finance Controller Agent.
    In Phase 2, an LLM agent implementation will analyze exceptions & ambiguous cases.
    """

    @abstractmethod
    def analyze_exception(self, result: ReconciliationResultRecord, context: Dict[str, Any]) -> AIAgentRecommendation:
        """Analyze an individual exception record using multi-source financial evidence."""
        pass

    @abstractmethod
    def batch_process_exceptions(self, exceptions: List[ReconciliationResultRecord]) -> List[AIAgentRecommendation]:
        """Process a batch of unresolved/exception records."""
        pass

class MockPhase2AIAgent(AIFinanceAgentInterface):
    """
    Placeholder/Mock implementation demonstrating Phase 2 integration readiness.
    """

    def analyze_exception(self, result: ReconciliationResultRecord, context: Dict[str, Any]) -> AIAgentRecommendation:
        requires_escalation = result.confidence_score < 50.0
        action = "MANUAL_AUDIT" if requires_escalation else "AUTO_RESOLVE"

        return AIAgentRecommendation(
            order_id=result.order_id,
            recommended_status=result.status,
            ai_confidence_score=min(100.0, result.confidence_score + 10.0),
            reasoning_summary=f"AI Evaluated evidence for {result.order_id}. Explanation: {result.explanation}",
            evidence_compared=["Order Record", "Payment Gateway Webhook", "Bank Statement Line Item"],
            suggested_action=action,
            requires_human_escalation=requires_escalation
        )

    def batch_process_exceptions(self, exceptions: List[ReconciliationResultRecord]) -> List[AIAgentRecommendation]:
        return [self.analyze_exception(e, {}) for e in exceptions]

