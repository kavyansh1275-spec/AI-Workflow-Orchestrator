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
    def diagnose(self, error, location=""):
        return Diagnostic(type(error).__name__, str(error), location)

    def propose_fix(self, diagnostic):
        return DebugResult(
            diagnostic,
            "Inspect the failing operation and its inputs.",
            "Apply the smallest safe change, then verify again.",
        )
