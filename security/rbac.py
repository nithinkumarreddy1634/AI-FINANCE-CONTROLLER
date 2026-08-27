"""
Role-Based Access Control (RBAC) Module
Defines roles (Finance Analyst, Finance Reviewer, Administrator) and permissions.
"""

from enum import Enum
from typing import Set

class UserRole(str, Enum):
    ANALYST = "FINANCE_ANALYST"
    REVIEWER = "FINANCE_REVIEWER"
    ADMINISTRATOR = "ADMINISTRATOR"

class Permission(str, Enum):
    VIEW_TRANSACTIONS = "VIEW_TRANSACTIONS"
    RUN_INVESTIGATION = "RUN_INVESTIGATION"
    SUBMIT_HUMAN_REVIEW = "SUBMIT_HUMAN_REVIEW"
    RESOLVE_EXCEPTION = "RESOLVE_EXCEPTION"
    MANAGE_SETTINGS = "MANAGE_SETTINGS"
    MANAGE_KNOWLEDGE_BASE = "MANAGE_KNOWLEDGE_BASE"

ROLE_PERMISSIONS = {
    UserRole.ANALYST: {
        Permission.VIEW_TRANSACTIONS,
        Permission.RUN_INVESTIGATION
    },
    UserRole.REVIEWER: {
        Permission.VIEW_TRANSACTIONS,
        Permission.RUN_INVESTIGATION,
        Permission.SUBMIT_HUMAN_REVIEW,
        Permission.RESOLVE_EXCEPTION
    },
    UserRole.ADMINISTRATOR: {
        Permission.VIEW_TRANSACTIONS,
        Permission.RUN_INVESTIGATION,
        Permission.SUBMIT_HUMAN_REVIEW,
        Permission.RESOLVE_EXCEPTION,
        Permission.MANAGE_SETTINGS,
        Permission.MANAGE_KNOWLEDGE_BASE
    }
}

class RBACManager:
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        allowed = ROLE_PERMISSIONS.get(role, set())
        return permission in allowed

