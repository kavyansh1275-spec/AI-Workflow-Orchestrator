from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class VerificationResult:
    name: str
    passed: bool
    evidence: str

class VerificationEngine:
    def __init__(self): self.checks: dict[str,Callable[[],bool]]={}
    def register(self,name,check):
        if not name.strip(): raise ValueError("Check name is required")
        self.checks[name]=check
    def verify(self) -> tuple[VerificationResult,...]:
        out=[]
        for name,check in self.checks.items():
            try: passed=bool(check()); evidence="passed" if passed else "failed"
            except Exception as exc: passed=False; evidence=f"error:{type(exc).__name__}"
            out.append(VerificationResult(name,passed,evidence))
        return tuple(out)
