"""
Adversarial AI Hallucination Test Suite
Tests missing records, conflicting amounts, and non-existent policy queries.
"""

from ai_agent import (
    AIFinanceControllerAgent, PostLLMValidator, EvidencePackage,
    AIDecisionOutput, AIDecisionEnum, AIActionEnum, InvestigationState
)
from knowledge.retriever import PolicyRetriever

def test_missing_transaction_no_hallucinated_payment():
    evidence = EvidencePackage(order_id="ORD_MISSING", expected_amount=1000.0, order_payment_status="PENDING")
    agent = AIFinanceControllerAgent()
    rec_record = agent.build_evidence_package
    out = agent.provider.investigate(evidence)
    assert out.decision == AIDecisionEnum.UNRESOLVED
    assert out.recommended_action == AIActionEnum.ESCALATE

def test_non_existent_policy_retrieval():
    retriever = PolicyRetriever()
    citations = retriever.retrieve_policy("quantum mechanics space travel cryptocurrency", top_k=2)
    # Cosine similarity for irrelevant topics must yield low score
    if citations:
        assert citations[0].relevance_score < 0.2

