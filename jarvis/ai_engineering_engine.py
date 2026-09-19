from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable

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

@dataclass(frozen=True)
class EvaluationReport:
    metric: str
    value: float
    sample_count: int
    notes: tuple[str, ...]

class AIEngineeringEngine:
    """Dependency-free AI engineering planner, dataset inspector and evaluator."""

    def plan_model(self, task: str, architecture: str = "transformer") -> ModelPlan:
        task = task.strip() or "general AI task"
        architecture = architecture.strip().lower() or "transformer"
        components = {
            "transformer": ("tokenization", "embeddings", "attention", "output head"),
            "neural_network": ("input layer", "hidden layers", "activation", "output layer"),
            "rag": ("document loader", "chunker", "embeddings", "retriever", "generator"),
            "agent": ("planner", "tool registry", "executor", "verifier", "memory"),
        }.get(architecture, ("data pipeline", "model", "evaluation", "deployment"))
        return ModelPlan(task, architecture, components,
            ("define baseline", "hold out validation data", "measure task-specific metrics"),
            ("data leakage", "overfitting", "invalid evaluation", "unsafe or unreliable outputs"))

    def inspect_dataset(self, data: Any) -> DatasetReport:
        warnings: list[str] = []
        rows = columns = None
        missing = duplicates = 0
        if isinstance(data, list):
            rows = len(data)
            if data and all(isinstance(x, dict) for x in data):
                keys = set().union(*(x.keys() for x in data))
                columns = len(keys)
                missing = sum(1 for x in data for k in keys if x.get(k) is None)
                normalized = [json.dumps(x, sort_keys=True, default=str) for x in data]
                duplicates = len(normalized) - len(set(normalized))
            elif data:
                warnings.append("Expected a list of objects for tabular inspection")
        elif isinstance(data, dict):
            columns = len(data)
            warnings.append("Dictionary supplied; row count cannot be inferred")
        else:
            warnings.append("Unsupported dataset type")
        if rows == 0: warnings.append("Dataset is empty")
        if missing: warnings.append("Missing values detected")
        if duplicates: warnings.append("Duplicate rows detected")
        return DatasetReport(type(data).__name__, rows, columns, missing, duplicates, tuple(dict.fromkeys(warnings)))

    @staticmethod
    def validate_training_config(config: dict[str, Any]) -> list[str]:
        if not isinstance(config, dict): return ["Training configuration must be a dictionary"]
        errors = []
        for key in ("epochs", "batch_size"):
            value = config.get(key)
            if value is not None and (not isinstance(value, int) or value <= 0):
                errors.append(f"{key} must be a positive integer")
        value = config.get("learning_rate")
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0):
            errors.append("learning_rate must be positive and finite")
        value = config.get("validation_split")
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < value < 1):
            errors.append("validation_split must be between 0 and 1")
        return errors

    @staticmethod
    def classification_accuracy(predictions: Iterable[Any], labels: Iterable[Any]) -> EvaluationReport:
        predicted, actual = list(predictions), list(labels)
        if not predicted or not actual:
            raise ValueError("predictions and labels must not be empty")
        if len(predicted) != len(actual):
            raise ValueError("predictions and labels must have equal length")
        correct = sum(p == y for p, y in zip(predicted, actual))
        return EvaluationReport("accuracy", correct / len(actual), len(actual), ("Exact-match classification metric.",))

    @staticmethod
    def regression_mae(predictions: Iterable[float], targets: Iterable[float]) -> EvaluationReport:
        predicted, actual = list(predictions), list(targets)
        if not predicted or not actual or len(predicted) != len(actual):
            raise ValueError("prediction and target sequences must be non-empty and equal length")
        errors = [abs(float(p) - float(y)) for p, y in zip(predicted, actual)]
        return EvaluationReport("mae", sum(errors) / len(errors), len(actual), ("Lower values indicate smaller absolute error.",))

    @staticmethod
    def rag_pipeline_plan() -> tuple[str, ...]:
        return ("load documents", "normalize text", "chunk documents", "create embeddings",
                "store vectors with metadata", "retrieve relevant chunks", "generate grounded answer", "evaluate retrieval and grounding")

    @staticmethod
    def validate_rag_config(config: dict[str, Any]) -> list[str]:
        errors = []
        if not isinstance(config, dict): return ["RAG configuration must be a dictionary"]
        for key in ("chunk_size", "top_k"):
            value = config.get(key)
            if value is not None and (not isinstance(value, int) or value <= 0):
                errors.append(f"{key} must be a positive integer")
        if config.get("top_k", 1) > 100:
            errors.append("top_k is unusually large")
        return errors

    @staticmethod
    def to_dict(value: ModelPlan | DatasetReport | EvaluationReport) -> dict[str, Any]:
        return asdict(value)
