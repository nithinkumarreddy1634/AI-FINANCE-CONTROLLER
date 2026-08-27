"""
Unit tests for Controlled Agent Tools & Registry.
"""

from ai_agent.tools import (
    ToolRegistry, calculate_amount_difference, calculate_date_difference, search_finance_policy
)

def test_tool_registry_list_and_execution():
    registry = ToolRegistry()
    tools_list = registry.list_tools()
    assert "calculate_amount_difference" in tools_list
    assert "search_finance_policy" in tools_list

    res = registry.execute_tool("calculate_amount_difference", expected=5000.0, actual=4500.0)
    assert res["status"] == "success"
    assert res["result"]["difference"] == 500.0
    assert res["result"]["variance_pct"] == 10.0

def test_date_difference_tool():
    res = calculate_date_difference("2026-02-10 10:00:00", "2026-02-12 10:00:00")
    assert res["days_difference"] == 2

def test_search_finance_policy_tool():
    policies = search_finance_policy("settlement timing window")
    assert isinstance(policies, list)

