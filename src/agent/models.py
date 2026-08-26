from abc import ABC, abstractmethod


class AIModel(ABC):
    """Base interface for models used by the support agent."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from a prompt."""
        raise NotImplementedError


class MockModel(AIModel):
    """Deterministic model used for testing without an API key."""

    def generate(self, prompt: str) -> str:
        return "I can help with your request."