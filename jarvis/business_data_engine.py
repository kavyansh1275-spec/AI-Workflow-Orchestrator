from __future__ import annotations
from dataclasses import dataclass
from statistics import mean
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class TrendPoint:
    period: str
    value: float
    change: float

class BusinessDataEngine:
    """Dependency-free normalization and trend analysis for business records."""
    def normalize(self, records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        result=[]
        for record in records:
            if not isinstance(record, Mapping): raise ValueError("Each business record must be a mapping")
            row={str(k).strip().lower(): v for k,v in record.items()}
            result.append(row)
        return result

    def numeric_series(self, records: Iterable[Mapping[str, Any]], field: str) -> list[float]:
        values=[]
        for row in self.normalize(records):
            if field in row and row[field] is not None:
                try: values.append(float(row[field]))
                except (TypeError,ValueError): continue
        return values

    def trend(self, periods: Iterable[str], values: Iterable[float]) -> tuple[TrendPoint, ...]:
        periods=list(periods); values=[float(v) for v in values]
        if len(periods)!=len(values): raise ValueError("periods and values must have equal length")
        result=[]; previous=None
        for period,value in zip(periods,values):
            change=0.0 if previous is None else value-previous
            result.append(TrendPoint(str(period),value,change)); previous=value
        return tuple(result)

    @staticmethod
    def average(values: Iterable[float]) -> float:
        values=list(values)
        return mean(float(v) for v in values) if values else 0.0
