from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeAnalysis:
    language: str
    valid: bool
    errors: tuple[str, ...]
    imports: tuple[str, ...]
    functions: tuple[str, ...]
    classes: tuple[str, ...]


class ProgrammingEngine:
    """Static programming assistant foundation; it never executes user code."""

    def analyze_python(self, source: str) -> CodeAnalysis:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            location = f"line {exc.lineno}, column {exc.offset}"
            return CodeAnalysis(
                language="python",
                valid=False,
                errors=(f"{exc.msg} ({location})",),
                imports=(),
                functions=(),
                classes=(),
            )

        imports = []
        functions = []
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return CodeAnalysis(
            language="python",
            valid=True,
            errors=(),
            imports=tuple(dict.fromkeys(imports)),
            functions=tuple(dict.fromkeys(functions)),
            classes=tuple(dict.fromkeys(classes)),
        )
