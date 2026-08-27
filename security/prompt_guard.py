"""
Prompt Injection Guard & Untrusted Payload Sanitizer
Prevents prompt injection attacks inside transaction references, metadata, or customer notes.
Wraps user-provided financial fields inside explicit XML block delimiters.
"""

import re
from typing import Dict, Any

class PromptInjectionGuard:
    DANGEROUS_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"mark\s+this\s+transaction\s+as\s+matched",
        r"system\s+override",
        r"you\s+are\s+now",
        r"disregard\s+all\s+rules",
        r"sudo",
        r"drop\s+table"
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        for pattern in cls.DANGEROUS_PATTERNS:
            cleaned = re.sub(pattern, "[FILTERED_INJECTION_ATTEMPT]", cleaned, flags=re.IGNORECASE)
        return cleaned

    @classmethod
    def wrap_untrusted_data(cls, field_name: str, value: Any) -> str:
        sanitized_val = cls.sanitize_text(str(value)) if value is not None else "N/A"
        return f"<{field_name}_untrusted>{sanitized_val}</{field_name}_untrusted>"

