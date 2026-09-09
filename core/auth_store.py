from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DB_PATH = Path(os.getenv("AUTH_DB_PATH", "data/auth.db"))


class AuthStore:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    hashed_password TEXT NOT NULL,
                    disabled INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    request TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                )"""
            )

    def create_user(self, username: str, hashed_password: str, created_at: str) -> bool:
        with self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO users(username, hashed_password, created_at) VALUES (?, ?, ?)",
                    (username, hashed_password, created_at),
                )
            except sqlite3.IntegrityError:
                return False
        return True

    def get_user(self, username: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT username, hashed_password, disabled, created_at FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def save_workflow(self, username: str, request: str, environment: str, result_json: str, created_at: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO workflows(username, request, environment, result_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (username, request, environment, result_json, created_at),
            )
            return int(cursor.lastrowid)

    def list_workflows(self, username: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, request, environment, result_json, created_at FROM workflows WHERE username = ? ORDER BY id DESC",
                (username,),
            ).fetchall()
        return [dict(row) for row in rows]
