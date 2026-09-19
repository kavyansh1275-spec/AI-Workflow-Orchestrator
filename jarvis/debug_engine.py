from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Diagnostic:
    error_type: str
    message: str
    location: str = ""

@dataclass(frozen=True)
class DebugResult:
    diagnostic: Diagnostic
    hypothesis: str
    fix: str

class DebugEngine:
    def diagnose(self,error: Exception,location="") -> Diagnostic:
        return Diagnostic(type(error).__name__,str(error),location)
    def propose_fix(self,diagnostic: Diagnostic) -> DebugResult:
        return DebugResult(diagnostic,f"Investigate {diagnostic.error_type} at {diagnostic.location or 'unknown location'}",
                           f"Review the failing operation and validate the smallest safe change.")
