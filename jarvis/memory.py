from collections import deque
from dataclasses import dataclass
from typing import Deque

from .database import Database


CATEGORIES = {
    "fact",
    "preference",
    "goal",
    "instruction",
    "project",
    "habit",
    "decision",
    "relationship",
    "temporary",
}


@dataclass
class MemoryItem:
    request: str
    skills: list[str]
    category: str = "temporary"


class Memory:
    def __init__(self, limit: int = 100, database: Database | None = None):
        self.items: Deque[MemoryItem] = deque(maxlen=limit)
        self.database = database

    def remember(
        self,
        request: str,
        skills: list[str],
        category: str = "temporary",
        persist: bool = True,
    ) -> None:
        if category not in CATEGORIES:
            category = "temporary"
        item = MemoryItem(request, list(skills), category)
        self.items.append(item)
        if persist and self.database is not None:
            self.database.add(request, ",".join(skills), category)

    def recent(self, n: int = 10) -> list[MemoryItem]:
        return list(self.items)[-max(1, n):]

    def search(self, term: str, n: int = 10) -> list[MemoryItem]:
        term = term.lower().strip()
        if not term:
            return []
        local = [item for item in self.items if term in item.request.lower()]
        if self.database is None:
            return local[-n:]
        rows = self.database.search(term, n)
        return [
            MemoryItem(request=row[0], skills=[s for s in row[1].split(",") if s], category=row[2])
            for row in reversed(rows)
        ]
