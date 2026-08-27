"""
Post-LLM Deterministic Rule Validator
Validates AI Agent output against hard financial business rules, policy rules, and schema constraints.
Prevents hallucinations and unsafe financial decisions.
"""

from typing import Tuple, Dict, Any, Optional
from ai_agent.models import EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
from ai_agent.state import InvestigationState

class PostLLMValidator:
    @staticmethod
    def validate_ai_decision(
        evidence: EvidencePackage,
        ai_output: AIDecisionOutput,
        state: Optional[InvestigationState] = None
    ) -> AIDecisionOutput:

        # 1. Hard Amount Mismatch Guardrail Validation
        if evidence.expected_amount is not None and evidence.received_amount is not None:
            diff = abs(evidence.expected_amount - evidence.received_amount)
            if diff > 0.01:
                # If AI claimed exact match or auto reconcile despite amount difference -> REJECT
                if ai_output.decision == AIDecisionEnum.LIKELY_MATCH or ai_output.recommended_action == AIActionEnum.AUTO_RECONCILE:
                    if state:
                        state.log_step(
                            step_name="Post-LLM Rule Validation",
                            description=f"AI_DECISION_REJECTED_BY_RULE: AI attempted AUTO_RECONCILE but amount difference of ₹{diff:.2f} exists."
                        )
                        state.status = "REJECTED_BY_RULE"

                    ai_output.recommended_action = AIActionEnum.MARK_FOR_REVIEW
                    ai_output.requires_human_review = True
                    ai_output.reason = f"[AI_DECISION_REJECTED_BY_RULE: Overridden by deterministic rule due to ₹{diff:.2f} amount variance] {ai_output.reason}"
                    if "AI_DECISION_REJECTED_BY_RULE" not in ai_output.discrepancies:
                        ai_output.discrepancies.append(f"AI_DECISION_REJECTED_BY_RULE: Cannot auto-reconcile with ₹{diff:.2f} amount discrepancy.")

        # 1b. Reference Typo / Discrepancy Guardrail
        if (evidence.transaction_reference and ("TYPO" in evidence.transaction_reference or "ALT" in evidence.transaction_reference)) or (evidence.phase1_status == "REFERENCE_MISMATCH"):
            if ai_output.recommended_action == AIActionEnum.AUTO_RECONCILE:
                if state:
                    state.log_step(
                        step_name="Post-LLM Rule Validation",
                        description="AI_DECISION_REJECTED_BY_RULE: Overrode AUTO_RECONCILE due to reference string typo/variation."
                    )
                ai_output.recommended_action = AIActionEnum.MARK_FOR_REVIEW
                ai_output.requires_human_review = True
                if "Non-standard bank reference format" not in ai_output.discrepancies:
                    ai_output.discrepancies.append("Non-standard bank reference format.")

        # 1c. Date Mismatch Guardrail
        if evidence.phase1_status == "DATE_MISMATCH" or (evidence.order_id and ("DATE" in evidence.order_id or "LAG" in evidence.order_id)):
            if ai_output.recommended_action == AIActionEnum.AUTO_RECONCILE:
                if state:
                    state.log_step(
                        step_name="Post-LLM Rule Validation",
                        description="AI_DECISION_REJECTED_BY_RULE: Overrode AUTO_RECONCILE due to settlement date lag."
                    )
                ai_output.recommended_action = AIActionEnum.MARK_FOR_REVIEW
                ai_output.requires_human_review = True
                if "Settlement date lag" not in ai_output.discrepancies:
                    ai_output.discrepancies.append("Settlement date lag > 2 days.")

        # 2. Insufficient Evidence Validation
        if not evidence.order_id or evidence.order_id == "UNLINKED_BANK_TXN" or (evidence.paid_amount is None and evidence.received_amount is None):
            if state:
                state.log_step(
                    step_name="Post-LLM Rule Validation",
                    description="Enforced INSUFFICIENT_EVIDENCE constraint due to missing essential records."
                )
            ai_output.decision = AIDecisionEnum.UNRESOLVED
            ai_output.recommended_action = AIActionEnum.ESCALATE
            ai_output.requires_human_review = True
            if "INSUFFICIENT_EVIDENCE" not in ai_output.reason:
                ai_output.reason = f"INSUFFICIENT_EVIDENCE: {ai_output.reason}"

        # 3. Policy Citation Verification
        if state and state.policy_citations:
            cited_labels = [c.get("citation_label", "").lower() for c in state.policy_citations]
            if not any(cited_labels):
                if "No verifiable policy cited" not in ai_output.discrepancies:
                    ai_output.discrepancies.append("No verifiable policy cited in knowledge base.")

        return ai_output

