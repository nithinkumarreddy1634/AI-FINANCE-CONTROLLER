"""
Confidence-Based Policy Engine
Maps AI decision confidence scores to actionable financial policies.
Thresholds are fully configurable.
"""

from dataclasses import dataclass
from ai_agent.models import AIActionEnum, AIDecisionOutput

@dataclass
class PolicyConfig:
    high_confidence_threshold: float = 90.0
    medium_confidence_threshold: float = 70.0

class PolicyEngine:
    def __init__(self, config: Optional[PolicyConfig] = None):
        self.config = config or PolicyConfig()

    def evaluate_policy(self, decision_output: AIDecisionOutput) -> AIDecisionOutput:
        conf = decision_output.confidence

        if conf >= self.config.high_confidence_threshold:
            # High confidence: allow AUTO_RECONCILE if no hard safety flags exist
            decision_output.recommended_action = AIActionEnum.AUTO_RECONCILE
            decision_output.requires_human_review = False
        elif conf >= self.config.medium_confidence_threshold:
            # Medium confidence: MARK_FOR_REVIEW
            decision_output.recommended_action = AIActionEnum.MARK_FOR_REVIEW
            decision_output.requires_human_review = True
        else:
            # Low confidence: ESCALATE
            decision_output.recommended_action = AIActionEnum.ESCALATE
            decision_output.requires_human_review = True

        return decision_output

