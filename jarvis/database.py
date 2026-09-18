import sqlite3
from pathlib import Path

class Database:
    def __init__(self,path: str = "jarvis_memory.db"):
        self.path=Path(path)
        self._init()

    def _init(self):
        if str(self.path)==":memory:":
            self._memory_connection=sqlite3.connect(":memory:")
            self._create(self._memory_connection)
            return
        with sqlite3.connect(self.path) as db: self._create(db)

    @staticmethod
    def _create(db):
        db.execute("""CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, request TEXT NOT NULL,
            skills TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'temporary',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        columns={row[1] for row in db.execute("PRAGMA table_info(memories)").fetchall()}
        if "category" not in columns: db.execute("ALTER TABLE memories ADD COLUMN category TEXT NOT NULL DEFAULT 'temporary'")
        if "created_at" not in columns: db.execute("ALTER TABLE memories ADD COLUMN created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
        db.commit()

    def _connect(self):
        return self._memory_connection if hasattr(self,"_memory_connection") else sqlite3.connect(self.path)

    def add(self,request,skills,category="temporary"):
        db=self._connect()
        db.execute("INSERT INTO memories(request,skills,category) VALUES (?,?,?)",(request,skills,category)); db.commit()
        if db is not self._memory_connection if hasattr(self,"_memory_connection") else False: db.close()

    def recent(self,limit=10):
        db=self._connect()
        rows=db.execute("SELECT request,skills,category,created_at FROM memories ORDER BY id DESC LIMIT ?",(max(1,limit),)).fetchall()
        if db is not getattr(self,"_memory_connection",None): db.close()
        return rows

    def search(self,term,limit=10):
        db=self._connect(); rows=db.execute("SELECT request,skills,category,created_at FROM memories WHERE request LIKE ? ORDER BY id DESC LIMIT ?",(f"%{term}%",max(1,limit))).fetchall()
        if db is not getattr(self,"_memory_connection",None): db.close()
        return rows
