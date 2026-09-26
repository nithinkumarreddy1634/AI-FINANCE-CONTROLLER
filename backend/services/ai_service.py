"""
AI Service Layer
Orchestrates AI Finance Controller investigations, audit log persistence, and evaluation metrics.
"""

from typing import List, Dict, Any, Optional
from ai_agent import (
    AIFinanceControllerAgent, AuditLogManager, AIEvaluator,
    AIDecisionOutput, HumanReviewInput, AuditRecord
)
from backend.services.recon_service import ReconciliationService
from reconciliation.models import ReconciliationStatus

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            import os
            from ai_agent.providers.llm_provider import LLMAIProvider
            from ai_agent.providers.mock_provider import MockAIProvider
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                provider = LLMAIProvider(api_key=openrouter_key, provider_name="openrouter")
            else:
                provider = MockAIProvider()
            cls._instance.agent = AIFinanceControllerAgent(provider=provider)
            cls._instance.audit_manager = AuditLogManager()
            cls._instance.recon_service = ReconciliationService()
            cls._instance.ai_investigations_cache: Dict[str, AIDecisionOutput] = {}
        return cls._instance

    def investigate_all_exceptions(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        results = self.recon_service.latest_results
        if not results:
            self.recon_service.initialize_default_run()
            results = self.recon_service.latest_results

        exceptions = [r for r in results if r.status != ReconciliationStatus.MATCHED]

        if not force_refresh and self.ai_investigations_cache and len(self.ai_investigations_cache) == len(exceptions):
            if len(self.audit_manager.audit_logs) >= len(self.ai_investigations_cache):
                return [out.to_dict() for out in self.ai_investigations_cache.values()]

        from ai_agent.providers.mock_provider import MockAIProvider
        if isinstance(self.agent.provider, MockAIProvider):
            investigations = self.agent.batch_investigate(exceptions)
        else:
            orig_provider = self.agent.provider
            self.agent.provider = MockAIProvider()
            try:
                investigations = self.agent.batch_investigate(exceptions)
            finally:
                self.agent.provider = orig_provider

        output_list = []
        self.ai_investigations_cache.clear()
        for rule_record, ai_out in zip(exceptions, investigations):
            self.ai_investigations_cache[ai_out.order_id] = ai_out
            audit_entry = self.audit_manager.log_investigation(rule_record, ai_out)
            output_list.append(ai_out.to_dict())

        return output_list

    def investigate_transaction(self, order_id: str) -> Optional[Dict[str, Any]]:
        results = self.recon_service.latest_results
        if not results:
            self.recon_service.initialize_default_run()
            results = self.recon_service.latest_results

        target_record = None
        for r in results:
            if r.order_id == order_id or r.transaction_id == order_id or r.bank_transaction_id == order_id:
                target_record = r
                break

        if not target_record:
            return None

        ai_out = self.agent.investigate_exception(target_record)
        self.ai_investigations_cache[ai_out.order_id] = ai_out
        self.audit_manager.log_investigation(target_record, ai_out)

        return ai_out.to_dict()

    def get_investigation_by_id(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        audit_log = self.audit_manager.get_log_by_id(investigation_id)
        if audit_log:
            return audit_log.to_dict()
        return None

    def record_human_review(self, investigation_id: str, review_input: HumanReviewInput) -> Optional[Dict[str, Any]]:
        updated_audit = self.audit_manager.record_human_review(investigation_id, review_input)
        if updated_audit:
            return updated_audit.to_dict()
        return None

    def get_metrics(self) -> Dict[str, Any]:
        all_records = self.recon_service.latest_results
        if not all_records:
            self.recon_service.initialize_default_run()
            all_records = self.recon_service.latest_results

        cached_investigations = list(self.ai_investigations_cache.values())
        if not cached_investigations:
            self.investigate_all_exceptions()
            cached_investigations = list(self.ai_investigations_cache.values())

        return AIEvaluator.evaluate_performance(all_records, cached_investigations)

    def get_audit_trail(self, order_id: Optional[str] = None) -> List[Dict[str, Any]]:
        logs = self.audit_manager.get_logs(order_id)
        return [log.to_dict() for log in logs]
