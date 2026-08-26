from dataclasses import dataclass, field


@dataclass
class AgentResponse:
    answer: str
    action: str
    sources: list[str] = field(default_factory=list)
    requires_input: bool = False

    def __getitem__(self, key):
        """Allow backward-compatible dictionary-style access."""
        return getattr(self, key)

    def get(self, key, default=None):
        """Provide dictionary-like .get() compatibility."""
        return getattr(self, key, default)


def make_response(
    answer: str,
    action: str,
    sources: list[str] | None = None,
    requires_input: bool = False,
) -> AgentResponse:
    return AgentResponse(
        answer=answer,
        action=action,
        sources=sources or [],
        requires_input=requires_input,
    )