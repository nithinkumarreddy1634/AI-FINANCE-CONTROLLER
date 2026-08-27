"""
Agent Investigation State & Timeline Tracker
Tracks step-by-step investigation state, tool executions, policy citations, and timestamps.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class TimelineEvent:
    timestamp: str
    step_name: str
    description: str
    tool_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "timestamp": self.timestamp,
            "step_name": self.step_name,
            "description": self.description
        }
        if self.tool_used:
            res["tool_used"] = self.tool_used
        if self.data:
            res["data"] = self.data
        return res

@dataclass
class InvestigationState:
    investigation_id: str
    transaction_id: str
    order_id: str
    status: str = "IN_PROGRESS"
    evidence_collected: bool = False
    policies_retrieved: bool = False
    analysis_completed: bool = False
    confidence: float = 0.0
    final_decision: str = "UNRESOLVED"
    recommended_action: str = "ESCALATE"
    timeline: List[TimelineEvent] = field(default_factory=list)
    policy_citations: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    candidate_comparisons: List[Dict[str, Any]] = field(default_factory=list)

    def log_step(self, step_name: str, description: str, tool_used: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        ts = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        event = TimelineEvent(
            timestamp=ts,
            step_name=step_name,
            description=description,
            tool_used=tool_used,
            data=data
        )
        self.timeline.append(event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "investigation_id": self.investigation_id,
            "transaction_id": self.transaction_id,
            "order_id": self.order_id,
            "status": self.status,
            "evidence_collected": self.evidence_collected,
            "policies_retrieved": self.policies_retrieved,
            "analysis_completed": self.analysis_completed,
            "confidence": self.confidence,
            "final_decision": self.final_decision,
            "recommended_action": self.recommended_action,
            "timeline": [t.to_dict() for t in self.timeline],
            "policy_citations": self.policy_citations,
            "tool_calls": self.tool_calls,
            "candidate_comparisons": self.candidate_comparisons
        }

