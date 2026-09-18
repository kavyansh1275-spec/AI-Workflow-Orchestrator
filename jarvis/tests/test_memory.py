import tempfile
import unittest

from jarvis.database import Database
from jarvis.memory import Memory


class TestMemory(unittest.TestCase):
    def test_memory_persists_and_searches(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(f"{tmp}/memory.db")
            memory = Memory(database=db)
            memory.remember("Kav prefers Python", ["programming"], "preference")
            self.assertEqual(memory.recent(1)[0].category, "preference")
            found = memory.search("Python")
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].request, "Kav prefers Python")

    def test_unknown_category_becomes_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(database=Database(f"{tmp}/memory.db"))
            memory.remember("temporary note", [], "not-a-category")
            self.assertEqual(memory.recent(1)[0].category, "temporary")


if __name__ == "__main__":
    unittest.main()
