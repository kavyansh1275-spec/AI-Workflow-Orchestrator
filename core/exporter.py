from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.v10 import V10Run


class RunExporter:
    """Persist completed V10 runs as portable JSON reports."""

    def export(self, run: V10Run, directory: str | Path = "artifacts") -> Path:
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{run.run_id}.json"
        payload: dict[str, Any] = run.model_dump(mode="json")
        target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return target
