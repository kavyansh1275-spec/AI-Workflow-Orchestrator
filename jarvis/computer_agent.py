from __future__ import annotations
from .agent_engine import AgentEngine, Tool
from .computer_tool_engine import ComputerToolEngine

def create_computer_agent(workspace=".", dry_run=True, max_steps=8) -> AgentEngine:
    computer = ComputerToolEngine(workspace, dry_run=dry_run)
    agent = AgentEngine(max_steps=max_steps)
    for name, handler in computer.tool_map().items():
        agent.register_tool(Tool(name, f"Computer tool: {name}", handler))
    return agent
