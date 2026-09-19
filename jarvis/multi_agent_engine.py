from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class AgentRole:
    name: str
    responsibility: str

@dataclass(frozen=True)
class AgentMessage:
    sender: str
    receiver: str
    content: str

class MultiAgentCoordinator:
    """Deterministic coordinator for bounded specialist-agent workflows."""

    DEFAULT_ROLES = (
        AgentRole("planner", "break a goal into ordered tasks"),
        AgentRole("researcher", "collect and summarize relevant evidence"),
        AgentRole("builder", "produce an implementation plan or artifact"),
        AgentRole("verifier", "check outputs against explicit criteria"),
    )

    def __init__(self, max_messages: int = 12):
        self.max_messages = max(1, max_messages)
        self.roles = {r.name: r for r in self.DEFAULT_ROLES}
        self.handlers: dict[str, Callable[[str], str]] = {}

    def register_handler(self, role: str, handler: Callable[[str], str]) -> None:
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        self.handlers[role] = handler

    def delegate(self, goal: str, roles: tuple[str, ...] | None = None) -> tuple[AgentMessage, ...]:
        selected = roles or ("planner", "builder", "verifier")
        messages = []
        for role in selected:
            if role not in self.roles:
                continue
            messages.append(AgentMessage("coordinator", role, goal))
            if len(messages) >= self.max_messages:
                break
        return tuple(messages)

    def run(self, goal: str, roles: tuple[str, ...] | None = None) -> tuple[AgentMessage, ...]:
        messages = []
        for message in self.delegate(goal, roles):
            handler = self.handlers.get(message.receiver)
            content = handler(message.content) if handler else f"Role {message.receiver} prepared its task."
            messages.append(AgentMessage(message.receiver, "coordinator", content))
            if len(messages) >= self.max_messages:
                break
        return tuple(messages)
