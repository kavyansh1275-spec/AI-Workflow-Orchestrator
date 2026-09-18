from collections import deque
from dataclasses import dataclass
from typing import Deque

@dataclass
class MemoryItem:
    request: str
    skills: list[str]

class Memory:
    def __init__(self, limit: int = 100):
        self.items: Deque[MemoryItem] = deque(maxlen=limit)
    def remember(self, request: str, skills: list[str]) -> None:
        self.items.append(MemoryItem(request, list(skills)))
    def recent(self, n: int = 10) -> list[MemoryItem]:
        return list(self.items)[-n:]
