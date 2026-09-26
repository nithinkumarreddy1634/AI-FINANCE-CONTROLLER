"""
LLM AI Provider Implementation
Invokes OpenRouter / OpenAI / Gemini LLM API with structured financial reasoning,
strict JSON schema validation, timeout handling, and automatic fallback to MockAIProvider on failure.
"""

import json
import os
import re
import uuid
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

from ai_agent.models import EvidencePackage, AIDecisionOutput, AIDecisionEnum, AIActionEnum
from ai_agent.providers.base import AIProvider
from ai_agent.providers.mock_provider import MockAIProvider

class LLMAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, provider_name: str = "openrouter", model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.provider_name = provider_name
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.fallback_provider = MockAIProvider()

    def investigate(self, evidence: EvidencePackage) -> AIDecisionOutput:
        # If no key configured, cleanly run deterministic mock provider
        if not self.api_key or self.provider_name == "mock":
            return self.fallback_provider.investigate(evidence)

        try:
            return self._call_openrouter_api(evidence)
        except Exception as e:
            # Safe financial fallback on network or API failure
            fallback_res = self.fallback_provider.investigate(evidence)
            fallback_res.reason = f"[AI Engine: {self.model} | Fallback Active: {str(e)[:120]}] {fallback_res.reason}"
            return fallback_res

    def _call_openrouter_api(self, evidence: EvidencePackage) -> AIDecisionOutput:
        investigation_id = f"AI-{uuid.uuid4().hex[:6].upper()}"
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        prompt = f"""
Financial Transaction Evidence Package:
- Order ID: {evidence.order_id}
- Customer ID: {evidence.customer_id}
- Expected Amount: ₹{evidence.expected_amount}
- Gateway Paid Amount: {f'₹{evidence.paid_amount}' if evidence.paid_amount is not None else 'None (Missing)'}
- Bank Received Amount: {f'₹{evidence.received_amount}' if evidence.received_amount is not None else 'None (Missing)'}
- Gateway Payment Status: {evidence.gateway_payment_status}
- Bank Settlement Status: {evidence.bank_status}
- Payment Date: {evidence.payment_date}
- Bank Settlement Date: {evidence.transaction_date}
- Bank Transaction Reference: {evidence.transaction_reference}
- Rule Engine Status: {evidence.phase1_status} (Score: {evidence.phase1_confidence}%)
- Discrepancies Detected: {', '.join(evidence.detected_discrepancies) if evidence.detected_discrepancies else 'None'}
"""

        system_msg = """You are an expert AI Finance Controller specializing in automated payment reconciliation.
Your role is to investigate discrepancies between Customer Orders, Payment Gateway webhooks, and Bank Settlements.
Follow standard financial compliance:
1. If amounts match exactly, reference is verified, and date is within 3 days -> LIKELY_MATCH with recommended_action AUTO_RECONCILE.
2. If bank settlement is less than expected amount -> check if difference is consistent with gateway processing fee deduction (e.g. 1-3%) vs a customer partial payment.
3. If gateway payment or bank settlement is missing entirely -> ESCALATE.
4. If ambiguous reference typo or lag > 2 days -> MARK_FOR_REVIEW.
5. NEVER invent unverified funds or ignore missing records.

You MUST respond strictly with a valid JSON object with EXACTLY these keys:
{
  "decision": "LIKELY_MATCH" | "AMOUNT_MISMATCH" | "DATE_MISMATCH" | "DUPLICATE" | "PARTIAL_MATCH" | "UNRESOLVED" | "MISSING_PAYMENT" | "MISSING_BANK_TRANSACTION",
  "confidence": <float between 0.0 and 100.0>,
  "reason": "<clear concise financial explanation>",
  "evidence": ["<verified fact 1>", "<verified fact 2>"],
  "discrepancies": ["<discrepancy 1>"],
  "recommended_action": "AUTO_RECONCILE" | "MARK_FOR_REVIEW" | "ESCALATE",
  "requires_human_review": <true or false>
}"""

        req_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-finance-controller.vercel.app",
            "X-Title": "Smart Financial Reconciliation System"
        }

        req = urllib.request.Request(url, data=json.dumps(req_body).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw_content = data["choices"][0]["message"]["content"].strip()

        # Extract JSON substring if wrapped in markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_content)
        clean_json = json_match.group(1).strip() if json_match else raw_content

        parsed = json.loads(clean_json)

        # Parse and sanitize decision enum
        dec_str = str(parsed.get("decision", "UNRESOLVED")).upper()
        decision_enum = AIDecisionEnum.UNRESOLVED
        for e in AIDecisionEnum:
            if e.value == dec_str or e.name == dec_str:
                decision_enum = e
                break

        # Parse and sanitize action enum
        act_str = str(parsed.get("recommended_action", "MARK_FOR_REVIEW")).upper()
        action_enum = AIActionEnum.MARK_FOR_REVIEW
        for a in AIActionEnum:
            if a.value == act_str or a.name == act_str:
                action_enum = a
                break

        conf = float(parsed.get("confidence", 85.0))
        # Normalize if model returned 0.0 - 1.0 instead of 0 - 100
        if 0.0 <= conf <= 1.0:
            conf = conf * 100.0
        conf = min(max(conf, 0.0), 100.0)

        reason = str(parsed.get("reason", f"AI investigation completed via {self.model}."))
        ev_list = parsed.get("evidence", [f"Verified via {self.model}"])
        if isinstance(ev_list, str):
            ev_list = [ev_list]

        disc_list = parsed.get("discrepancies", [])
        if isinstance(disc_list, str):
            disc_list = [disc_list]

        requires_review = bool(parsed.get("requires_human_review", action_enum != AIActionEnum.AUTO_RECONCILE))

        return AIDecisionOutput(
            order_id=evidence.order_id,
            decision=decision_enum,
            confidence=round(conf, 1),
            reason=f"[OpenRouter: {self.model}] {reason}",
            evidence=ev_list,
            discrepancies=disc_list,
            recommended_action=action_enum,
            requires_human_review=requires_review,
            investigation_id=investigation_id,
            timestamp=ts
        )
