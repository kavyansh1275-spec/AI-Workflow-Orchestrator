from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ToolResult:
    ok: bool
    operation: str
    output: str

class ComputerToolEngine:
    """Safe computer tools with explicit workspace, command, and app allowlists."""
    DEFAULT_COMMANDS = frozenset({"python", "git", "node", "npm"})
    DEFAULT_APPS = frozenset({"notepad.exe", "calc.exe"})

    def __init__(self, workspace: str | Path = ".", dry_run: bool = True,
                 allowed_commands=None, allowed_apps=None):
        self.workspace = Path(workspace).resolve()
        self.dry_run = dry_run
        self.allowed_commands = frozenset(allowed_commands or self.DEFAULT_COMMANDS)
        self.allowed_apps = frozenset(a.lower() for a in (allowed_apps or self.DEFAULT_APPS))

    def _path(self, value: str) -> Path:
        path = (self.workspace / value).resolve()
        if path != self.workspace and self.workspace not in path.parents:
            raise ValueError("Path escapes the configured workspace")
        return path

    def list_files(self, relative=".") -> ToolResult:
        path = self._path(relative)
        if not path.is_dir(): return ToolResult(False, "list_files", "Not a directory")
        return ToolResult(True, "list_files", "\n".join(sorted(p.name for p in path.iterdir())))

    def read_file(self, relative, max_chars=100_000) -> ToolResult:
        path = self._path(relative)
        if not path.is_file(): return ToolResult(False, "read_file", "File not found")
        if max_chars <= 0: return ToolResult(False, "read_file", "max_chars must be positive")
        try: return ToolResult(True, "read_file", path.read_text(encoding="utf-8")[:max_chars])
        except UnicodeDecodeError: return ToolResult(False, "read_file", "File is not UTF-8 text")

    def write_file(self, relative, content) -> ToolResult:
        path = self._path(relative)
        if self.dry_run: return ToolResult(True, "write_file", f"DRY RUN: would write {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return ToolResult(True, "write_file", f"Wrote {path}")

    def run_command(self, command, timeout=20) -> ToolResult:
        parts = command.strip().split()
        if not parts or parts[0].lower() not in self.allowed_commands:
            return ToolResult(False, "run_command", "Command is not allowlisted")
        if timeout <= 0: return ToolResult(False, "run_command", "timeout must be positive")
        if self.dry_run: return ToolResult(True, "run_command", f"DRY RUN: would run {command}")
        try:
            p = subprocess.run(parts, cwd=self.workspace, capture_output=True, text=True,
                               timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return ToolResult(False, "run_command", "Command timed out")
        return ToolResult(p.returncode == 0, "run_command", (p.stdout + p.stderr).strip())

    def launch_app(self, executable) -> ToolResult:
        name = Path(executable).name.lower()
        if name not in self.allowed_apps: return ToolResult(False, "launch_app", "Application is not allowlisted")
        if self.dry_run: return ToolResult(True, "launch_app", f"DRY RUN: would launch {name}")
        try:
            subprocess.Popen([executable])
            return ToolResult(True, "launch_app", f"Launched {name}")
        except OSError:
            return ToolResult(False, "launch_app", "Unable to launch application")

    def tool_map(self):
        return {
            "list_files": lambda arg: self.list_files(arg).output,
            "read_file": lambda arg: self.read_file(arg).output,
            "write_file": lambda arg: self.write_file(arg, "").output,
            "run_command": lambda arg: self.run_command(arg).output,
            "launch_app": lambda arg: self.launch_app(arg).output,
        }
