"""
Controlled Tool Registry
Manages tool definitions, execution dispatch, and logging.
"""

from typing import Dict, Any, Callable, List, Optional
from ai_agent.tools import finance_tools

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            "get_order": finance_tools.get_order,
            "get_payment": finance_tools.get_payment,
            "get_bank_transaction": finance_tools.get_bank_transaction,
            "search_transactions": finance_tools.search_transactions,
            "compare_transactions": finance_tools.compare_transactions,
            "calculate_amount_difference": finance_tools.calculate_amount_difference,
            "calculate_date_difference": finance_tools.calculate_date_difference,
            "search_finance_policy": finance_tools.search_finance_policy,
            "get_reconciliation_result": finance_tools.get_reconciliation_result
        }

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' is not registered."}
        try:
            result = self.tools[tool_name](**kwargs)
            return {"tool_name": tool_name, "status": "success", "result": result}
        except Exception as e:
            return {"tool_name": tool_name, "status": "error", "error": str(e)}

