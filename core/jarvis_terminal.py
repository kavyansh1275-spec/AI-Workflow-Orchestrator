from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class TerminalEvent:
    stream: str
    line: str


class JarvisTerminal:
    """Run real local commands and stream stdout/stderr to a caller."""

    def __init__(self, cwd: str | Path | None = None) -> None:
        self.cwd = Path(cwd or ".").resolve()

    def run(
        self,
        command: list[str],
        emit: Callable[[TerminalEvent], None] | None = None,
        timeout: int = 300,
    ) -> int:
        process = subprocess.Popen(
            command,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            if emit:
                emit(TerminalEvent("stdout", line.rstrip()))
        return process.wait(timeout=timeout)

    def run_shell(
        self,
        command: str,
        emit: Callable[[TerminalEvent], None] | None = None,
        timeout: int = 300,
    ) -> int:
        process = subprocess.Popen(
            command,
            cwd=self.cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            if emit:
                emit(TerminalEvent("stdout", line.rstrip()))
        return process.wait(timeout=timeout)
