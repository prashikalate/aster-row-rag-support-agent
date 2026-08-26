from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    """Small session-scoped memory for relevant conversation context."""

    messages: list[dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append({
            "role": role,
            "content": content,
        })

    def recent(self, limit: int = 6) -> list[dict[str, str]]:
        return self.messages[-limit:]

    def clear(self) -> None:
        self.messages.clear()