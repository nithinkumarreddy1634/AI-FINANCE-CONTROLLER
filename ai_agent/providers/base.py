"""
AI Provider Base Abstract Class
Defines the interface for AI Providers (Mock, OpenAI, Gemini, etc.)
"""

from abc import ABC, abstractmethod
from ai_agent.models import EvidencePackage, AIDecisionOutput

class AIProvider(ABC):
    """
    Abstract interface for AI Providers investigating reconciliation exceptions.
    """

    @abstractmethod
    def investigate(self, evidence: EvidencePackage) -> AIDecisionOutput:
        """
        Analyze an evidence package and return structured AI decision output.
        """
        pass

