"""
Hybrid Decision Controller & Safety Validator
Combines Phase 1 deterministic rules with Phase 2 AI reasoning and policy evaluation.
Enforces non-negotiable financial safety constraints.
"""

from typing import Tuple, List, Optional
from ai_agent.models import EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
from ai_agent.policy import PolicyEngine, PolicyConfig

class HybridDecisionEngine:
    def __init__(self, policy_engine: Optional[PolicyEngine] = None):
        self.policy_engine = policy_engine or PolicyEngine()

    def process(self, evidence: EvidencePackage, raw_ai_output: AIDecisionOutput) -> AIDecisionOutput:
        # Step 1: Apply Confidence Policy Engine
        processed_output = self.policy_engine.evaluate_policy(raw_ai_output)

        # Step 2: Enforce Hard Safety Constraints

        # CONSTRAINT A: Amount Discrepancy Hard Guardrail
        # If expected amount and bank received amount differ, AI CANNOT declare exact MATCHED or AUTO_RECONCILE
        if evidence.expected_amount is not None and evidence.received_amount is not None:
            diff = abs(evidence.expected_amount - evidence.received_amount)
            if diff > 0.01:
                if processed_output.decision == AIDecisionEnum.LIKELY_MATCH or processed_output.recommended_action == AIActionEnum.AUTO_RECONCILE:
                    processed_output.recommended_action = AIActionEnum.MARK_FOR_REVIEW
                    processed_output.requires_human_review = True
                    if "Amount discrepancy hard guardrail enforced" not in processed_output.discrepancies:
                        processed_output.discrepancies.append(f"Amount discrepancy hard guardrail enforced: difference of ₹{diff:.2f} prevents full auto-reconciliation.")

        # CONSTRAINT B: Missing Evidence Safety Guardrail
        if not evidence.order_id or (evidence.paid_amount is None and evidence.received_amount is None):
            processed_output.decision = AIDecisionEnum.UNRESOLVED
            processed_output.recommended_action = AIActionEnum.ESCALATE
            processed_output.requires_human_review = True
            if "INSUFFICIENT_EVIDENCE" not in processed_output.reason:
                processed_output.reason = f"INSUFFICIENT_EVIDENCE: {processed_output.reason}"

        return processed_output

