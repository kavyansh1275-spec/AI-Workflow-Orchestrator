import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str = "jarvis_memory.db"):
        self.path = Path(path)
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request TEXT NOT NULL,
                    skills TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'temporary',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {
                row[1]
                for row in db.execute("PRAGMA table_info(memories)").fetchall()
            }
            if "category" not in columns:
                db.execute(
                    "ALTER TABLE memories ADD COLUMN category TEXT NOT NULL DEFAULT 'temporary'"
                )
            if "created_at" not in columns:
                db.execute(
                    "ALTER TABLE memories ADD COLUMN created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
                )
            db.commit()

    def add(self, request: str, skills: str, category: str = "temporary") -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO memories(request, skills, category) VALUES (?, ?, ?)",
                (request, skills, category),
            )
            db.commit()

    def recent(self, limit: int = 10) -> list[tuple]:
        with sqlite3.connect(self.path) as db:
            return db.execute(
                "SELECT request, skills, category, created_at "
                "FROM memories ORDER BY id DESC LIMIT ?",
                (max(1, limit),),
            ).fetchall()

    def search(self, term: str, limit: int = 10) -> list[tuple]:
        with sqlite3.connect(self.path) as db:
            like = f"%{term}%"
            return db.execute(
                "SELECT request, skills, category, created_at "
                "FROM memories WHERE request LIKE ? ORDER BY id DESC LIMIT ?",
                (like, max(1, limit)),
            ).fetchall()
