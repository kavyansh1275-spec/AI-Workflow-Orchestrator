from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ToolResult:
    ok: bool
    operation: str
    output: str

class ComputerToolEngine:
    """Safe computer-tool foundation with explicit workspace and command allowlists."""

    def __init__(self, workspace: str | Path = ".", dry_run: bool = True):
        self.workspace = Path(workspace).resolve()
        self.dry_run = dry_run
        self.allowed_commands = {"python", "git", "node", "npm"}

    def _path(self, value: str) -> Path:
        path = (self.workspace / value).resolve()
        if path != self.workspace and self.workspace not in path.parents:
            raise ValueError("Path escapes the configured workspace")
        return path

    def list_files(self, relative: str = ".") -> ToolResult:
        path = self._path(relative)
        if not path.is_dir():
            return ToolResult(False, "list_files", "Not a directory")
        names = sorted(p.name for p in path.iterdir())
        return ToolResult(True, "list_files", "\n".join(names))

    def read_file(self, relative: str, max_chars: int = 100_000) -> ToolResult:
        path = self._path(relative)
        if not path.is_file():
            return ToolResult(False, "read_file", "File not found")
        if max_chars <= 0:
            return ToolResult(False, "read_file", "max_chars must be positive")
        return ToolResult(True, "read_file", path.read_text(encoding="utf-8")[:max_chars])

    def write_file(self, relative: str, content: str) -> ToolResult:
        path = self._path(relative)
        if self.dry_run:
            return ToolResult(True, "write_file", f"DRY RUN: would write {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return ToolResult(True, "write_file", f"Wrote {path}")

    def run_command(self, command: str, timeout: int = 20) -> ToolResult:
        parts = command.strip().split()
        if not parts or parts[0].lower() not in self.allowed_commands:
            return ToolResult(False, "run_command", "Command is not allowlisted")
        if timeout <= 0:
            return ToolResult(False, "run_command", "timeout must be positive")
        if self.dry_run:
            return ToolResult(True, "run_command", f"DRY RUN: would run {command}")
        try:
            completed = subprocess.run(
                parts, cwd=self.workspace, capture_output=True, text=True,
                timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "run_command", "Command timed out")
        output = (completed.stdout + completed.stderr).strip()
        return ToolResult(completed.returncode == 0, "run_command", output)

    def launch_app(self, executable: str) -> ToolResult:
        name = os.path.basename(executable)
        if name.lower() not in {"notepad.exe", "calc.exe"}:
            return ToolResult(False, "launch_app", "Application is not allowlisted")
        if self.dry_run:
            return ToolResult(True, "launch_app", f"DRY RUN: would launch {name}")
        try:
            subprocess.Popen([executable])
            return ToolResult(True, "launch_app", f"Launched {name}")
        except OSError:
            return ToolResult(False, "launch_app", "Unable to launch application")
