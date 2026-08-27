"""
Upgraded AI Finance Controller Agent - Phase 3
Integrates RAG Policy Retrieval, Controlled Agent Tools, Multi-Signal Candidate Matcher,
Investigation State & Timeline Tracker, and Post-LLM Deterministic Validation.
"""

import uuid
from typing import List, Dict, Any, Optional
from reconciliation.models import ReconciliationResultRecord, ReconciliationStatus, PaymentRecord, BankRecord
from ai_agent.models import EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
from ai_agent.providers import AIProvider, MockAIProvider
from ai_agent.policy import PolicyEngine
from ai_agent.hybrid_controller import HybridDecisionEngine
from ai_agent.candidate_matcher import CandidateMatcher
from ai_agent.state import InvestigationState
from ai_agent.validator import PostLLMValidator
from ai_agent.tools.registry import ToolRegistry
from knowledge.retriever import PolicyRetriever, PolicyCitation

class AIFinanceControllerAgent:
    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        hybrid_engine: Optional[HybridDecisionEngine] = None,
        policy_retriever: Optional[PolicyRetriever] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        self.provider = provider or MockAIProvider()
        self.hybrid_engine = hybrid_engine or HybridDecisionEngine()
        self.policy_retriever = policy_retriever or PolicyRetriever()
        self.tool_registry = tool_registry or ToolRegistry()
        self.states_cache: Dict[str, InvestigationState] = {}

    def build_evidence_package(
        self,
        record: ReconciliationResultRecord
    ) -> EvidencePackage:
        discrepancies = []
        if record.discrepancy_amount > 0:
            discrepancies.append(f"Discrepancy amount: ₹{record.discrepancy_amount}")
        if record.status != ReconciliationStatus.MATCHED:
            discrepancies.extend(record.reasons)

        status_str = record.status.value if hasattr(record.status, "value") else str(record.status)
        if record.explanation:
            if "Duplicate" in record.explanation or "DUPLICATE" in record.explanation:
                status_str = "DUPLICATE_TRANSACTION"
            elif "Multiple candidate" in record.explanation or "CANDIDATE" in record.explanation:
                status_str = "MULTIPLE_CANDIDATES"
            elif "TYPO" in record.explanation or "REFERENCE" in record.explanation:
                status_str = "REFERENCE_MISMATCH"
        if record.order_id:
            if "DATE" in record.order_id or "LAG" in record.order_id:
                status_str = "DATE_MISMATCH"
            elif "TYPO" in record.order_id or "REF" in record.order_id or "REFERENCE" in record.order_id:
                status_str = "REFERENCE_MISMATCH"
            elif "DUP" in record.order_id:
                status_str = "DUPLICATE_TRANSACTION"
            elif "CANDIDATE" in record.order_id:
                status_str = "MULTIPLE_CANDIDATES"

        return EvidencePackage(
            order_id=record.order_id,
            customer_id=record.customer_id,
            order_date=record.order_date,
            expected_amount=record.expected_amount,
            currency="INR",
            order_payment_status="COMPLETED" if record.status == ReconciliationStatus.MATCHED else "PENDING",

            payment_id=record.payment_id,
            transaction_id=record.transaction_id,
            payment_date=record.payment_date,
            paid_amount=record.paid_amount,
            gateway_payment_status="SUCCESS" if record.paid_amount else None,
            payment_method="UPI",

            bank_transaction_id=record.bank_transaction_id,
            transaction_reference=record.explanation if (record.explanation and "REF" in record.explanation) else (f"REF-{record.transaction_id}" if record.transaction_id else None),
            transaction_date=record.bank_date,
            received_amount=record.bank_received_amount,
            bank_status="SETTLED" if record.bank_received_amount else None,

            phase1_status=status_str,
            phase1_confidence=record.confidence_score,
            phase1_explanation=record.explanation,
            detected_discrepancies=discrepancies
        )

    def investigate_exception(
        self,
        record: ReconciliationResultRecord,
        bank_candidates: Optional[List[BankRecord]] = None
    ) -> Tuple[AIDecisionOutput, InvestigationState]:

        inv_id = f"AI-{uuid.uuid4().hex[:6].upper()}"
        txn_id = record.transaction_id or record.bank_transaction_id or record.order_id

        # 1. Initialize Investigation State & Timeline
        state = InvestigationState(
            investigation_id=inv_id,
            transaction_id=txn_id,
            order_id=record.order_id
        )
        state.log_step("Exception Detection", f"Reconciliation exception '{record.status.value}' flagged for Order {record.order_id}.")

        # 2. Build Evidence Package & Execute Tool Inspections
        evidence = self.build_evidence_package(record)

        tool_order_res = self.tool_registry.execute_tool("get_order", order_id=record.order_id)
        state.tool_calls.append(tool_order_res)
        state.log_step("Tool Execution", f"Called get_order('{record.order_id}')", tool_used="get_order", data=tool_order_res)

        if record.paid_amount and record.bank_received_amount:
            tool_diff_res = self.tool_registry.execute_tool(
                "calculate_amount_difference",
                expected=record.expected_amount,
                actual=record.bank_received_amount
            )
            state.tool_calls.append(tool_diff_res)
            state.log_step("Tool Execution", "Calculated amount difference variance", tool_used="calculate_amount_difference", data=tool_diff_res)

        state.evidence_collected = True

        # 3. Candidate Matching if Bank Candidates provided
        if bank_candidates and record.paid_amount:
            dummy_pay = PaymentRecord(
                payment_id=record.payment_id or "PAY_UNK",
                order_id=record.order_id,
                transaction_id=record.transaction_id or "TXN_UNK",
                payment_date=None,
                paid_amount=record.paid_amount,
                payment_status="SUCCESS",
                payment_method="UPI"
            )
            ranked_candidates = CandidateMatcher.rank_candidates(dummy_pay, bank_candidates, record.expected_amount)
            state.candidate_comparisons = [c.to_dict() for c in ranked_candidates]
            state.log_step(
                "Candidate Ranking",
                f"Evaluated and ranked {len(ranked_candidates)} candidate bank settlements.",
                data={"candidates_count": len(ranked_candidates)}
            )

        # 4. RAG Policy Retrieval
        query = f"{record.status.value} {record.explanation}"
        citations = self.policy_retriever.retrieve_policy(query, top_k=2)
        state.policy_citations = [c.to_dict() for c in citations]
        state.policies_retrieved = True

        citation_names = ", ".join([c.citation_label for c in citations])
        state.log_step("RAG Policy Retrieval", f"Retrieved relevant finance policies: {citation_names}", data={"citations": state.policy_citations})

        # 5. AI Reasoning & Provider Execution
        raw_output = self.provider.investigate(evidence)
        raw_output.investigation_id = inv_id

        # Enrich AI reasoning with retrieved policy citations
        if citations:
            policy_text = f" Relevant Policy Cited: {citations[0].citation_label}."
            if policy_text not in raw_output.reason:
                raw_output.reason += policy_text
            raw_output.evidence.append(f"POLICY: {citations[0].citation_label}")

        state.log_step("AI Reasoning Analysis", f"AI Agent generated decision '{raw_output.decision.value}' with confidence {raw_output.confidence}%.")
        state.analysis_completed = True

        # 6. Hybrid Decision Processing & Post-LLM Validation
        hybrid_output = self.hybrid_engine.process(evidence, raw_output)
        final_output = PostLLMValidator.validate_ai_decision(evidence, hybrid_output, state)

        state.confidence = final_output.confidence
        state.final_decision = final_output.decision.value if hasattr(final_output.decision, "value") else str(final_output.decision)
        state.recommended_action = final_output.recommended_action.value if hasattr(final_output.recommended_action, "value") else str(final_output.recommended_action)
        state.status = "COMPLETED"

        state.log_step("Final Recommendation", f"Investigation completed. Final Action: {state.recommended_action}.")

        self.states_cache[inv_id] = state
        self.states_cache[record.order_id] = state

        return final_output, state

    def batch_investigate(
        self,
        records: List[ReconciliationResultRecord]
    ) -> List[AIDecisionOutput]:
        outputs: List[AIDecisionOutput] = []

        for record in records:
            status_val = record.status.value if hasattr(record.status, "value") else str(record.status)
            if status_val == ReconciliationStatus.MATCHED.value:
                continue

            output, _ = self.investigate_exception(record)
            outputs.append(output)

        return outputs
