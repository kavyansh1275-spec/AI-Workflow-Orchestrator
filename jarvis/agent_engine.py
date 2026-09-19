from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable

from .memory import Memory, MemoryItem

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[[str], str]

@dataclass(frozen=True)
class AgentStep:
    step: int
    action: str
    result: str

@dataclass(frozen=True)
class AgentResult:
    goal: str
    steps: tuple[AgentStep, ...]
    success: bool
    stopped_reason: str

class AgentEngine:
    """Bounded agent loop with optional memory-aware planning."""
    def __init__(self, max_steps: int = 8, memory: Memory | None = None):
        self.max_steps = max(1, max_steps)
        self.tools: dict[str, Tool] = {}
        self.memory = memory

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def list_tools(self) -> tuple[str, ...]:
        return tuple(self.tools)

    def plan(self, goal: str, memory_context: Iterable[MemoryItem] | None = None) -> tuple[str, ...]:
        text = goal.strip()
        if not text:
            return ()
        context = list(memory_context) if memory_context is not None else (
            self.memory.search(text, 5) if self.memory else []
        )
        steps = ["understand goal"]
        if context:
            steps.append("apply relevant memory context")
        steps += ["select registered tools", "execute bounded steps", "verify result", "record outcome"]
        return tuple(steps)

    def execute(self, goal: str, tool_calls: list[tuple[str, str]]) -> AgentResult:
        steps: list[AgentStep] = []
        for index, (name, argument) in enumerate(tool_calls[:self.max_steps], 1):
            tool = self.tools.get(name)
            if tool is None:
                steps.append(AgentStep(index, f"tool:{name}", "Tool not registered"))
                return AgentResult(goal, tuple(steps), False, "unregistered_tool")
            try:
                result = str(tool.handler(argument))
            except Exception as exc:
                steps.append(AgentStep(index, f"tool:{name}", f"Tool error: {type(exc).__name__}"))
                return AgentResult(goal, tuple(steps), False, "tool_error")
            steps.append(AgentStep(index, f"tool:{name}", result))
        if not tool_calls:
            return AgentResult(goal, (), False, "no_tool_calls")
        if len(tool_calls) > self.max_steps:
            return AgentResult(goal, tuple(steps), False, "step_limit")
        success = self.verify(steps)
        if success and self.memory:
            self.memory.remember(goal, list(self.tools), "decision")
        return AgentResult(goal, tuple(steps), success, "completed")

    @staticmethod
    def verify(steps: list[AgentStep] | tuple[AgentStep, ...]) -> bool:
        return bool(steps) and all(
            not s.result.startswith(("Tool error:", "Tool not registered")) for s in steps
        )
