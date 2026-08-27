"""
Unit tests for Tool Security Policy and Role-Based Access Control (RBAC).
"""

from security import ToolSecurityPolicy, UserRole, Permission, RBACManager

def test_tool_security_policy_allowed_and_blocked():
    assert ToolSecurityPolicy.validate_tool_call("get_order", {"order_id": "ORD1"}) is True
    assert ToolSecurityPolicy.validate_tool_call("calculate_amount_difference", {"expected": 100, "actual": 90}) is True

    # Blocked tool / payload
    assert ToolSecurityPolicy.validate_tool_call("delete_database", {}) is False
    assert ToolSecurityPolicy.validate_tool_call("get_order", {"order_id": "ORD1; os.system('rm -rf')"}) is False

def test_rbac_permissions():
    assert RBACManager.has_permission(UserRole.ANALYST, Permission.VIEW_TRANSACTIONS) is True
    assert RBACManager.has_permission(UserRole.ANALYST, Permission.SUBMIT_HUMAN_REVIEW) is False

    assert RBACManager.has_permission(UserRole.REVIEWER, Permission.SUBMIT_HUMAN_REVIEW) is True
    assert RBACManager.has_permission(UserRole.ADMINISTRATOR, Permission.MANAGE_SETTINGS) is True

