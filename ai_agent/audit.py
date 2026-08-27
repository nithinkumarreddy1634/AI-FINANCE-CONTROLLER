"""
Audit Log Manager
Manages append-only immutable audit trail for AI investigations and human-in-the-loop decisions.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from ai_agent.models import AuditRecord, AIDecisionOutput, HumanReviewInput
from reconciliation.models import ReconciliationResultRecord

class AuditLogManager:
    _instance = None

    def __new__(cls, file_path: str = os.path.join("data", "audit_log.json")):
        if cls._instance is None:
            cls._instance = super(AuditLogManager, cls).__new__(cls)
            cls._instance.file_path = file_path
            cls._instance.audit_logs: List[AuditRecord] = []
            cls._instance._load_logs()
        elif file_path != cls._instance.file_path:
            cls._instance.file_path = file_path
            cls._instance.audit_logs = []
            cls._instance._load_logs()
        return cls._instance

    def _load_logs(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.audit_logs = [AuditRecord(**item) for item in data]
            except Exception as e:
                self.audit_logs = []

    def _save_logs(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([log.to_dict() for log in self.audit_logs], f, indent=2)

    def log_investigation(
        self,
        rule_record: ReconciliationResultRecord,
        ai_output: AIDecisionOutput
    ) -> AuditRecord:

        rule_decision = rule_record.status.value if hasattr(rule_record.status, "value") else str(rule_record.status)
        ai_decision = ai_output.decision.value if hasattr(ai_output.decision, "value") else str(ai_output.decision)
        rec_action = ai_output.recommended_action.value if hasattr(ai_output.recommended_action, "value") else str(ai_output.recommended_action)

        audit_entry = AuditRecord(
            investigation_id=ai_output.investigation_id,
            transaction_id=rule_record.transaction_id or rule_record.bank_transaction_id or rule_record.order_id,
            order_id=rule_record.order_id,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            rule_decision=rule_decision,
            rule_confidence=rule_record.confidence_score,
            ai_decision=ai_decision,
            ai_confidence=ai_output.confidence,
            recommended_action=rec_action,
            requires_human_review=ai_output.requires_human_review,
            evidence_summary=ai_output.evidence,
            ai_reason=ai_output.reason
        )

        self.audit_logs.append(audit_entry)
        self._save_logs()
        return audit_entry

    def record_human_review(
        self,
        investigation_id: str,
        review_input: HumanReviewInput
    ) -> Optional[AuditRecord]:

        target: Optional[AuditRecord] = None
        for log in self.audit_logs:
            if log.investigation_id == investigation_id:
                target = log
                break

        if not target:
            return None

        h_decision = review_input.decision.value if hasattr(review_input.decision, "value") else str(review_input.decision)

        target.human_decision = h_decision
        target.reviewer_name = review_input.reviewer_name
        target.reviewer_note = review_input.reviewer_note
        target.review_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        self._save_logs()
        return target

    def get_logs(self, order_id: Optional[str] = None) -> List[AuditRecord]:
        if order_id:
            return [log for log in self.audit_logs if log.order_id == order_id or log.transaction_id == order_id]
        return self.audit_logs

    def get_log_by_id(self, investigation_id: str) -> Optional[AuditRecord]:
        for log in self.audit_logs:
            if log.investigation_id == investigation_id:
                return log
        return None
