from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ModelPlan:
    task: str
    architecture: str
    components: tuple[str, ...]
    evaluation: tuple[str, ...]
    risks: tuple[str, ...]


@dataclass(frozen=True)
class DatasetReport:
    format: str
    rows: int | None
    columns: int | None
    missing_values: int
    duplicate_rows: int
    warnings: tuple[str, ...]


class AIEngineeringEngine:
    """Dependency-free AI engineering planner and dataset inspector."""

    def plan_model(self, task: str, architecture: str = "transformer") -> ModelPlan:
        task = task.strip() or "general AI task"
        architecture = architecture.strip().lower() or "transformer"
        components = {
            "transformer": ("tokenization", "embeddings", "attention", "output head"),
            "neural_network": ("input layer", "hidden layers", "activation", "output layer"),
            "rag": ("document loader", "chunker", "embeddings", "retriever", "generator"),
            "agent": ("planner", "tool registry", "executor", "verifier", "memory"),
        }.get(architecture, ("data pipeline", "model", "evaluation", "deployment"))
        evaluation = ("define baseline", "hold out validation data", "measure task-specific metrics")
        risks = ("data leakage", "overfitting", "invalid evaluation", "unsafe or unreliable outputs")
        return ModelPlan(task, architecture, components, evaluation, risks)

    def inspect_dataset(self, data: Any) -> DatasetReport:
        warnings: list[str] = []
        rows = columns = None
        missing = duplicates = 0

        if isinstance(data, list):
            rows = len(data)
            if data and isinstance(data[0], dict):
                keys = set().union(*(item.keys() for item in data if isinstance(item, dict)))
                columns = len(keys)
                for item in data:
                    if not isinstance(item, dict):
                        warnings.append("Mixed row types detected")
                        continue
                    missing += sum(1 for key in keys if item.get(key) is None)
                normalized = [json.dumps(item, sort_keys=True, default=str) for item in data]
                duplicates = len(normalized) - len(set(normalized))
            else:
                warnings.append("Expected a list of objects for tabular inspection")
        elif isinstance(data, dict):
            columns = len(data)
            warnings.append("Dictionary supplied; row count cannot be inferred")
        else:
            warnings.append("Unsupported dataset type")

        if rows == 0:
            warnings.append("Dataset is empty")
        if missing:
            warnings.append("Missing values detected")
        if duplicates:
            warnings.append("Duplicate rows detected")

        return DatasetReport(
            format=type(data).__name__,
            rows=rows,
            columns=columns,
            missing_values=missing,
            duplicate_rows=duplicates,
            warnings=tuple(dict.fromkeys(warnings)),
        )

    @staticmethod
    def validate_training_config(config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not isinstance(config, dict):
            return ["Training configuration must be a dictionary"]

        epochs = config.get("epochs")
        if epochs is not None and (not isinstance(epochs, int) or epochs <= 0):
            errors.append("epochs must be a positive integer")

        batch_size = config.get("batch_size")
        if batch_size is not None and (not isinstance(batch_size, int) or batch_size <= 0):
            errors.append("batch_size must be a positive integer")

        learning_rate = config.get("learning_rate")
        if learning_rate is not None and (not isinstance(learning_rate, (int, float)) or learning_rate <= 0):
            errors.append("learning_rate must be positive")

        if "validation_split" in config:
            split = config["validation_split"]
            if not isinstance(split, (int, float)) or not 0 < split < 1:
                errors.append("validation_split must be between 0 and 1")

        return errors

    @staticmethod
    def to_dict(value: ModelPlan | DatasetReport) -> dict[str, Any]:
        return asdict(value)
