from __future__ import annotations
from dataclasses import dataclass
from .agent_engine import AgentEngine
from .computer_tool_engine import ComputerToolEngine

@dataclass(frozen=True)
class BrowserResult:
    ok: bool
    operation: str
    output: str

class BrowserTool:
    """Safe browser abstraction: URL validation only; no unrestricted automation."""
    def __init__(self, dry_run=True):
        self.dry_run = dry_run

    def open_url(self, url: str) -> BrowserResult:
        if not (url.startswith("https://") or url.startswith("http://")):
            return BrowserResult(False, "open_url", "Only HTTP(S) URLs are allowed")
        if self.dry_run:
            return BrowserResult(True, "open_url", f"DRY RUN: would open {url}")
        return BrowserResult(True, "open_url", f"Browser handoff requested for {url}")

def create_v9_agent(workspace=".", dry_run=True, max_steps=8) -> AgentEngine:
    computer = ComputerToolEngine(workspace, dry_run=dry_run)
    browser = BrowserTool(dry_run=dry_run)
    agent = AgentEngine(max_steps=max_steps)
    for name, handler in computer.tool_map().items():
        agent.register_tool(__import__("jarvis.agent_engine", fromlist=["Tool"]).Tool(name, f"Computer tool: {name}", handler))
    agent.register_tool(__import__("jarvis.agent_engine", fromlist=["Tool"]).Tool(
        "open_url", "Open an HTTP(S) URL through the browser abstraction",
        lambda arg: browser.open_url(arg).output
    ))
    return agent
