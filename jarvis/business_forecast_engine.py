from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Forecast:
    periods: tuple[str, ...]
    values: tuple[float, ...]
    method: str

class BusinessForecastEngine:
    """Simple transparent baseline forecast; intentionally dependency-free."""
    def moving_average(self, values: Iterable[float], horizon: int = 3, window: int = 3) -> Forecast:
        values=[float(v) for v in values]
        if not values: raise ValueError("values must not be empty")
        if horizon < 1 or window < 1: raise ValueError("horizon and window must be positive")
        history=values[:]
        predicted=[]
        for _ in range(horizon):
            value=sum(history[-window:])/min(window,len(history))
            predicted.append(value); history.append(value)
        return Forecast(tuple(f"T+{i}" for i in range(1,horizon+1)),tuple(predicted),"moving_average")
