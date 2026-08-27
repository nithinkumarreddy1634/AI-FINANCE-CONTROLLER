"""
Tool Security Policy & Sandbox Guardrail
Restricts AI Agent tool execution to strictly approved read-only and analytical tools.
Blocks python eval/exec, shell commands, file deletions, or money movement operations.
"""

from typing import Set

class ToolSecurityPolicy:
    ALLOWED_TOOLS: Set[str] = {
        "get_order",
        "get_payment",
        "get_bank_transaction",
        "search_transactions",
        "compare_transactions",
        "calculate_amount_difference",
        "calculate_date_difference",
        "search_finance_policy",
        "get_reconciliation_result"
    }

    FORBIDDEN_KEYWORDS: Set[str] = {
        "exec", "eval", "system", "os.", "subprocess", "rm", "delete",
        "transfer_money", "refund", "write_file", "drop_db"
    }

    @classmethod
    def validate_tool_call(cls, tool_name: str, args: dict) -> bool:
        if tool_name not in cls.ALLOWED_TOOLS:
            return False

        # Verify arguments do not contain forbidden code execution payloads
        args_str = str(args).lower()
        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in args_str:
                return False

        return True

