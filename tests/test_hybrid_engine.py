"""
Unit tests for Hybrid Controller safety guardrails and policy threshold mapping.
"""

from ai_agent import (
    HybridDecisionEngine, PolicyEngine, PolicyConfig,
    EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
)

def test_policy_thresholds():
    engine = HybridDecisionEngine()
    evidence = EvidencePackage(order_id="ORD001", expected_amount=1000.0, paid_amount=1000.0, received_amount=1000.0)

    # High confidence -> AUTO_RECONCILE
    output_high = AIDecisionOutput(
        order_id="ORD001", decision=AIDecisionEnum.LIKELY_MATCH, confidence=95.0,
        reason="Match", evidence=[], discrepancies=[], recommended_action=AIActionEnum.MARK_FOR_REVIEW, requires_human_review=True
    )
    res_high = engine.process(evidence, output_high)
    assert res_high.recommended_action == AIActionEnum.AUTO_RECONCILE
    assert res_high.requires_human_review is False

    # Medium confidence -> MARK_FOR_REVIEW
    output_med = AIDecisionOutput(
        order_id="ORD001", decision=AIDecisionEnum.AMOUNT_MISMATCH, confidence=80.0,
        reason="Variance", evidence=[], discrepancies=[], recommended_action=AIActionEnum.AUTO_RECONCILE, requires_human_review=False
    )
    res_med = engine.process(evidence, output_med)
    assert res_med.recommended_action == AIActionEnum.MARK_FOR_REVIEW
    assert res_med.requires_human_review is True

    # Low confidence -> ESCALATE
    output_low = AIDecisionOutput(
        order_id="ORD001", decision=AIDecisionEnum.UNRESOLVED, confidence=50.0,
        reason="Unsure", evidence=[], discrepancies=[], recommended_action=AIActionEnum.MARK_FOR_REVIEW, requires_human_review=False
    )
    res_low = engine.process(evidence, output_low)
    assert res_low.recommended_action == AIActionEnum.ESCALATE
    assert res_low.requires_human_review is True

def test_amount_mismatch_safety_guardrail():
    """Ensure AI cannot output AUTO_RECONCILE when an amount discrepancy exists."""
    engine = HybridDecisionEngine()
    evidence = EvidencePackage(order_id="ORD002", expected_amount=5000.0, paid_amount=5000.0, received_amount=4500.0)

    raw_ai = AIDecisionOutput(
        order_id="ORD002", decision=AIDecisionEnum.LIKELY_MATCH, confidence=95.0,
        reason="Attempting auto reconcile despite difference", evidence=[], discrepancies=[],
        recommended_action=AIActionEnum.AUTO_RECONCILE, requires_human_review=False
    )

    result = engine.process(evidence, raw_ai)
    # Safety guardrail must override AUTO_RECONCILE to MARK_FOR_REVIEW
    assert result.recommended_action == AIActionEnum.MARK_FOR_REVIEW
    assert result.requires_human_review is True
    assert any("guardrail" in d.lower() for d in result.discrepancies)

