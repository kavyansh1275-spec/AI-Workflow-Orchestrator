import sqlite3
from pathlib import Path

class Database:
    def __init__(self, path: str = "jarvis_memory.db"):
        self.path = Path(path)
        self._init()
    def _init(self):
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, request TEXT NOT NULL, skills TEXT NOT NULL)")
            db.commit()
    def add(self, request: str, skills: str) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO memories(request, skills) VALUES (?, ?)", (request, skills))
            db.commit()
