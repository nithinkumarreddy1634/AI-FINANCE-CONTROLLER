"""
Unit tests for Post-LLM Deterministic Rule Validator & Hallucination Prevention.
"""

from ai_agent import (
    PostLLMValidator, EvidencePackage, AIDecisionOutput,
    AIDecisionEnum, AIActionEnum, InvestigationState
)

def test_post_llm_validator_rejects_invalid_auto_reconcile():
    evidence = EvidencePackage(
        order_id="ORD_HALLUCINATED",
        expected_amount=4200.0,
        paid_amount=4200.0,
        received_amount=3800.0,
        phase1_status="AMOUNT_MISMATCH"
    )

    state = InvestigationState(investigation_id="AI-VAL1", transaction_id="TXN1", order_id="ORD_HALLUCINATED")

    # Raw AI attempts to declare exact LIKELY_MATCH and AUTO_RECONCILE despite ₹400 variance
    raw_ai = AIDecisionOutput(
        order_id="ORD_HALLUCINATED",
        decision=AIDecisionEnum.LIKELY_MATCH,
        confidence=95.0,
        reason="AI mistakenly claims exact match",
        evidence=["Paid 4200"],
        discrepancies=[],
        recommended_action=AIActionEnum.AUTO_RECONCILE,
        requires_human_review=False
    )

    validated = PostLLMValidator.validate_ai_decision(evidence, raw_ai, state)

    # Post-LLM rule validator must REJECT decision and override AUTO_RECONCILE to MARK_FOR_REVIEW
    assert validated.recommended_action == AIActionEnum.MARK_FOR_REVIEW
    assert validated.requires_human_review is True
    assert "AI_DECISION_REJECTED_BY_RULE" in validated.reason
    assert state.status == "REJECTED_BY_RULE"

