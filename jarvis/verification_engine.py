from dataclasses import dataclass

@dataclass(frozen=True)
class VerificationResult:
    name: str
    passed: bool
    evidence: str

class VerificationEngine:
    def __init__(self):
        self.checks = {}

    def register(self, name, check):
        if not name.strip():
            raise ValueError("Check name is required")
        self.checks[name] = check

    def verify(self):
        results = []
        for name, check in self.checks.items():
            try:
                passed = bool(check())
                evidence = "passed" if passed else "failed"
            except Exception as exc:
                passed = False
                evidence = "error:" + type(exc).__name__
            results.append(VerificationResult(name, passed, evidence))
        return tuple(results)
